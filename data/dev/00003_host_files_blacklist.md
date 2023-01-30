---
id: 3
title: Host file as a blacklist
date: 2020-12-13
preview: |
  Using an simple text file to blacklist websites.
section: dev
tags:
  - networking
draft: false
---

[TOC]

The Hosts file is a plain-text file that maps human-readable hostnames (e.g. `google.com`) to IP addresses (the actual address needed to find a website).
It is an old-school method of resolving hostnames (or domain names), and has been used since the time of ARPANET.
It's still in use today (supplmenting better methods, i.e. DNS lookups), and typically it is the first process in the hostname resolution process.

The Hosts file is located:

- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **Linux**: `/etc/hosts`
- **OSX**: `/private/etc/hosts`

An example entry in the Hosts file looks like:

```
127.0.0.1 localhosts
```

Read aloud, this maps the hostname `localhosts` to the IP address `127.0.0.1`, i.e. loopback. So when you type `localhosts` in your browser, your system will
find that entry in your Hosts file and translate it to `127.0.0.1` accordingly.

## Why is it useful?

Some handy use-cases for the Hosts file:

- Provides a quick, easy way to map domains to IPs without having to change DNS records (e.g. when migrating to new servers)
- Can be used as a blacklist, filtering away known hostnames that are used for malware, spam, or other malicious activities.

## As a blacklist

By mapping domains to either `127.0.0.1` or `0.0.0.0`, you can effectively block any queries to the undesired domain name.

The two mappings will ultimately achieve the same result, but `0.0.0.0` is the better of the two:

- `127.0.0.1` is the loopback address; i.e. it will "loop back" to your own machine. This can be problematic for blacklisting since it may actually try to query your machine and either will bombard whatever webserver you are locally hosting, or be slowed down waiting for a timeout
- `0.0.0.0` is a non-routable meta-address used to designate an invalid, unknown or non-applicable target. In the [IANA IPv4 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml) it is listed as non-Forwardable.

### Publically maintained Host file blacklists

There are several publically available blacklists that you can use. These are large files that enumerate known domains which are used for ads or malware.

| List                     | #Entries | Comment                                                                                                                     | Source                                                                                                                                               |
|--------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| MVPS                     | ~9200    | One of the oldest hosts blocklists, available since 1998. It targets major parasites, hijackers and unwanted Adware/Spyware | [https://winhelp2002.mvps.org/](https://winhelp2002.mvps.org/)                                                                                       |
| 2o7.net                  | 1286     | Specialised to tracking one service, the notorious 207 service                                                              | [FadeMind's Repo](https://github.com/FadeMind/hosts.extras), [List](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts) |
| Ultimate.Hosts.Blacklist | >400,000 | Probably one of the largest blacklists available, however has been reported with **too many false-positives**               | [https://github.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist](https://github.com/Ultimate-Hosts-Blacklist/Ultimate.Hosts.Blacklist)         |

### Safety precautions

If you choose to use a Host file from a publically maintained blacklist, do some basic checks to ensure nothing malicious is going on. None of the lists above have anything malicious, but as an example of what **may** go wrong, [Malwarebytes blogged about a hosts file hijack](https://blog.malwarebytes.com/cybercrime/2016/09/hosts-file-hijacks/) which copied the MVPS host file and replaced the IP `0.0.0.0` with their own server. As a result, all domains that were intended to be blocked, were actually redirecting to their, likely, malicious server.

You can use something as simple as search-and-replace with regex to ensure you don't fall victim to this:

1. You could, for example, use Visual Studio Code's search with Regex and search for all lines that start with `0.0.0.0` (regex search string: `^0\.0\.0\.0.*$`). You can then select all occurances (`ctrl`+`shift`+`L`) and copy those lines over to your host file.

2. The alternative is to remove all lines that do not start with `0.0.0.0` using a negative lookahead after start-of-line: `^(?!0\.0\.0\.0).*\n*$` and replace all matches with nothing, then copying the remainding entries over to your hosts file.

    - `^` matches start of line
    - `(?!0\.0\.0\.0)` checks to see the `^` match is not followed by `0.0.0.0`
    - `.*` matches everything in-between `^` and `$` (i.e. the line)
    - `\n*` matches a newline if it exists


### Keeping things tidy

Publically available blacklists do not typically include `localhost` entries that your Host file will need for looping back.
On-top of that, it can be quite unwieldy to have tens of thousands of blacklist entries mixed up with your own entries (if you use the Host file for another use-case).

You can simply setup a scheduled job to fetch, filter and copy over the blacklist into your `/etc/hosts` (or wherever):

``` bash
#!/bin/bash

# MVPS
blacklist_source=https://winhelp2002.mvps.org/hosts.txt

host_file=/etc/hosts
host_local=~/hosts.local

# Fetch the blacklist
blacklist_swp="$host_file.blacklist"
wget -q $blacklist_source -O $blacklist_swp

if [ -f $blacklist_swp ]; then

    # Filters
    perl -p -i -e 's/^(?!0\.0\.0\.0).*\n$//' $blacklist_swp
    sed -i 's/\r//g' $blacklist_swp

    # Make a backup
    host_swp="$host_file.backup"
    cp $host_file $host_swp

    # Create the host file
    touch $host_file
    cat $host_local > $host_file

    # Copy over the blacklist
    printf "\n# BLACKLIST\n" >> $host_file
    cat $blacklist_swp >> $host_file

    rm $blacklist_swp

fi
```

You'll need to maintain your own `host.local` file that keeps your own mappings.

A linux `host.local` would look like this:

```
127.0.0.1	localhost

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```
