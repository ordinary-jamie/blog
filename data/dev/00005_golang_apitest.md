---
id: 5
title: GoLang script for API Testing
date: 2021-08-29
preview: |
  A quick GoLang gist to do API testing against HTTP files
section: dev
tags:
  - testing
  - web
draft: false
type: blog
---

[TOC]

## What this gist will do

A simple GoLang script that will recursively find all `.http` files in some directory, parse and call them with the
specified headers and body (optional), and compare it against a response pair (status code, headers and body).

Simple usage demo:

```
$ ls tests/
    200.http  400.http

$ go run test.go -t tests/
    ✓ API:tests\200.http
    ✘ tests\400.http: Failed because 'Header mismatch for request-id'
            Expected: '1ab2c3d4'
            Actual: 'Some-Request-ID'

    1 Errors caught
    exit status 1
```

## Background

I know there are a lot of test frameworks like Mocha and Jest, but I've recently discovered an incredibly
handy tool for making REST calls from VSCode, [Rest Client by Huachao Mao](https://marketplace.visualstudio.com/items?itemName=humao.rest-client).

Basically, you write up the HTTP request in a `.http` file and the extension will give you a `"Send Request"` option.
The request might look like this:

``` http
GET http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=730&count=3&maxlength=300&format=json HTTP/1.1
User-Agent: PostmanRuntime/7.28.3
Accept: application/json
```

I enjoy this extension a lot because it offers a great middle-ground between ease of packaging up the request (just a plain `.http` file with no metadata, as in Postman)
and readability and ease of use (unlike, say a cURL command).

So I wanted to use these files to specify a series of contract tests against a developed microservice for basic API testing.

## Implementation Overview

It's a pretty simple Go script, with three key components/steps:

1. Define a test case type that has the HTTP request to make and the expected response. We define a method to compare the two here.
2. Define a parsing function that parses `.http` files into the test case type (with the `net/http` Request and expected response)
3. Recursively walk through a directory to find all `.http` files

### 1. Test Case Type in Go

{{< tldr "Define a test case type that has the HTTP request to make and the expected response. We define a method to compare the two here" >}}

Our test type is a pretty simple; just a simple request, response container with a `Name string` for reporting:

``` go
type HttpTestCase struct {
    Name string
    Request *http.Request
    Expected struct {
        StatusCode int
        Headers map[string]string
        Body string
    }
}
```

First, we define a couple of basic pass/fail methods for the type:

``` go
func (tc *HttpTestCase) Pass() bool {
    fmt.Printf("✓ API:%s\n", tc.Name)
    return true
}

func (tc *HttpTestCase) Fail(reason string, expected interface{}, actual interface{}) bool {
    fmt.Printf("✘ %s: Failed because '%s'\n\tExpected: '%v'\n\tActual: '%v'\n", tc.Name, reason, expected, actual)
    return false
}
```

We then implement the test method for this type

``` go
import (
    "net/http"
    "strings"
    "io/ioutil"
)

func (tc *HttpTestCase) Test(client *http.Client) bool {
    if tc.Request == nil {
        return tc.Fail("Could not parse test case", "", "")
    }

    // We have the consumer pass the client so they can
    // make configurations as needed.
    resp, _ := client.Do(tc.Request)

    // Compare status codes
    if resp.StatusCode != tc.Expected.StatusCode {
        return tc.Fail("Incorrect status code", tc.Expected.StatusCode, resp.StatusCode)
    }

    // Compare the headers.
    // Note we are only comparing a subset here,
    // Hence only iterating over the expected headers.
    for header, expected := range tc.Expected.Headers {
        if actual := strings.ToLower(resp.Header.Get(header)); actual != expected {
            return tc.Fail("Header mismatch for " + header, expected, actual)
        }
    }

    // Compare body.
    // There's room for improvement here, as it is a strict comparison
    // Removing whitespace would make this more robust.
    if tc.Expected.Body != "" {
        bodyBytes, err := ioutil.ReadAll(resp.Body)
        if err != nil {
            return tc.Fail("Failed to parse body", tc.Expected.Body, "")
        }
        actualBody := strings.TrimSpace(string(bodyBytes))
        if actualBody != tc.Expected.Body {
            return tc.Fail("Body does not match", tc.Expected.Body, actualBody)
        }
    }

    return tc.Pass()
}
```


### 2. Parsing HTTP files

{{< tldr "Define a parsing function that parses `.http` files into the test case type (with the `net/http` Request and expected response)">}}

HTTP files can be broken down into 6 parts as described in the table. Each of these parts are
sequential, one after the other in the file:



| Capture Group(s)                          | Example                             | Regex                                                                         |
|-------------------------------------------|-------------------------------------|-------------------------------------------------------------------------------|
| Request method and URL                    | `GET http://something.com HTTP/1.1` | <code>^(GET&#124;POST&#124;PUT&#124;DELETE)\s+([^\s]*)\s?(HTTP/1.1)?\n</code> |
| Request key-value header pairs (optional) | `Accept: application/json`          | `((.*:.*\n)*)`                                                                |
| Request body (optional)                   | `{"result": "something"}`           | <code>((.&#124;\n)*)</code>                                                   |
| Response code                             | `HTTP/1.1 200 OK`                   | `HTTP/1.1\s?([0-9]*)\s?.*\n`                                                  |
| Response key-value header pairs           |                                     | `((.*:.*\n)*)`                                                                |
| Response body (optional)                  |                                     | <code>((.&#124;\n)*)</code>                                                   |

Before we implement this regex in GoLang, we first define some useful utility functions

First our headers capture group `((.*:.*\n)*)` is just a dump of `(.*:.*\n)` groups, so we need to convert this into a map

``` go
import "strings"

func parseHeaders(headers string) map[string]string {
    ret := make(map[string]string)
    for _, header_line := range strings.Split(headers, "\n") {
        header_part := strings.Split(header_line, ":")
        if len(header_part) != 2 {
            continue
        }
        ret[strings.ToLower(strings.TrimSpace(header_part[0]))] = strings.ToLower(strings.TrimSpace(header_part[1]))
    }
    return ret
}
```

Next, This `MatchGroup` type is a simple wrapper over GoLang's standard type [`regexp.Regexp`](https://pkg.go.dev/regexp).
The purpose of this wrapper is just to make using the package a slight easier with the named capture groups.

``` go
import (
    "regexp"
    "strings"
)

type MatchGroup struct {
    matches []string
    re *regexp.Regexp
}

func (m *MatchGroup) Get(key string) string {
    return strings.TrimSpace(m.matches[m.re.SubexpIndex(key)])
}

func (m *MatchGroup) Match(target string) bool {
    if m.re.MatchString(target) {
        m.matches = m.re.FindStringSubmatch(target)
        return true
    } else {
        return false
    }
}
```

Now we can parse our HTTP file using the structure we discussed into the `HttpTestCase` type we defined earlier

``` go
import (
    "bytes"
    "io/ioutil"
    "log"
    "net/http"
    "regexp"
    "strconv"
)

func parse_http_file(fname string) *HttpTestCase {

    file, err := ioutil.ReadFile(fname)
    if err != nil {
        log.Fatal(err)
    }

    // I just concatenated the patterns in the table above here
    // and gave the important capture groups some names with the ?P<Name> syntax
    http_file_format := regexp.MustCompile(`^(?P<Method>GET|POST|PUT|DELETE)\s+(?P<URL>[^\s]*)\s?(HTTP/1.1)?\n(?P<ReqHeader>(.*:.*\n)*)(?P<ReqBody>(.|\n)*)HTTP/1.1\s?(?P<StatusCode>[0-9]*)\s?.*\n(?P<RespHeader>(.*:.*\n)*)(?P<RespBody>(.|\n)*)`)

    // Matching and Getting
    tc := &HttpTestCase{Name: fname}
    mg := &MatchGroup{re: http_file_format}

    if mg.Match(string(file)) {
        reqBody := []byte(mg.Get("ReqBody"))
        tc.Request, _ = http.NewRequest(mg.Get("Method"), mg.Get("URL"), bytes.NewBuffer(reqBody))

        for k,v := range parseHeaders(mg.Get("ReqHeader")) {
            tc.Request.Header.Set(k,v)
        }

        tc.Expected.StatusCode, _ = strconv.Atoi(mg.Get("StatusCode"))
        tc.Expected.Headers = parseHeaders(mg.Get("RespHeader"))
        tc.Expected.Body = mg.Get("RespBody")
    }
    return tc
}
```

### 3. Walk Dir for HTTP Files

{{< tldr "Recursively walk through a directory to find all `.http` files" >}}

For walking over a directory and finding all files with an extension, I'll shamelessly grab a [StackOverflow answer by Tim Cooper](https://stackoverflow.com/questions/55300117/how-do-i-find-all-files-that-have-a-certain-extension-in-go-regardless-of-depth) (Thanks, Tim):

``` go
import "path/filepath"

func WalkMatch(root, pattern string) ([]string, error) {
    var matches []string
    err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        if info.IsDir() {
            return nil
        }
        if matched, err := filepath.Match(pattern, filepath.Base(path)); err != nil {
            return err
        } else if matched {
            matches = append(matches, path)
        }
        return nil
    })
    if err != nil {
        return nil, err
    }
    return matches, nil
}
```

## Putting it all together

We put this all together in a main function which accepts a `-t` flag for the directory containing our tests:

``` go
import (
    "flag"
    "fmt"
    "net/http"
    "os"
)

func main() {
    testFiles := flag.String("t", "./data/", "path to test files")
    flag.Parse()

    client := &http.Client{}
    n_err := 0
    files, _ := WalkMatch(*testFiles, "*.http")
    for _, file := range files {
        tc := parse_http_file(file)
        if ok := tc.Test(client); !ok {
            n_err += 1
        }
    }

    if n_err > 0 {
        fmt.Printf("\n\n%d Errors caught\n", n_err)
        os.Exit(1)
    } else {
        os.Exit(0)
    }
}
```

## Demonstration

Here are the complete files for this demo:

- [test.go](/blog/golang-api-test/test.go), a compilation of what we just went through
- [demoservice.go](/blog/golang-api-test/demoservice.go), a basic HTTP server to test
- [tests/200.http](/blog/golang-api-test/200.http), a 200-OK API test
- [tests/400.http](/blog/golang-api-test/400.http), a 400-BAD-REQUEST API test

Usage:

``` bash
go run demoservice.go

go run test.go -t tests/
```

### The demo Files

#### `demoservice.go`
This exposes the `GET /hello` endpoint, and expects the header `Accept: text/plain` or it will throw a `HTTP 400 BAD-REQUEST`:

``` go
package main

import (
	"net/http"
	"github.com/go-chi/chi/v5"
)

func main() {
	r := chi.NewRouter()

	r.Get("/hello", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Request-Id", "Some-Request-ID")
		w.Header().Set("Service-Name", "Demo")

		accept := r.Header.Get("Accept")
		if accept != "text/plain" {
			w.WriteHeader(400)
			w.Write([]byte("Must set accept to text/plain"))
			return
		}
		w.Write([]byte("Hello, World!"))
	})

	http.ListenAndServe(":3000", r)
}
```

#### `tests/200.http`

``` http
GET http://localhost:3000/hello HTTP/1.1
Accept: text/plain


HTTP/1.1 200 OK
Request-Id: Some-Request-ID
Service-Name: Demo

Hello, World!
```

#### `tests/400.http`

``` http
GET http://localhost:3000/hello HTTP/1.1
Accept: application/json


HTTP/1.1 400 Bad Request
Request-Id: Some-Request-ID
Service-Name: Demo

Must set accept to text/plain
```

#### `test.go`

``` go
package main

import (
    "bytes"
    "flag"
    "log"
    "fmt"
    "os"
    "path/filepath"
    "net/http"
    "regexp"
    "io/ioutil"
    "strings"
    "strconv"
)

func main() {
    testFiles := flag.String("t", "./data/", "path to test files")
    flag.Parse()

    client := &http.Client{}
    n_err := 0
    files, _ := WalkMatch(*testFiles, "*.http")
    for _, file := range files {
        tc := parse_http_file(file)
        if ok := tc.Test(client); !ok {
            n_err += 1
        }
    }

    if n_err > 0 {
        fmt.Printf("\n\n%d Errors caught\n", n_err)
        os.Exit(1)
    } else {
        os.Exit(0)
    }
}

type HttpTestCase struct {
    Name string
    Request *http.Request
    Expected struct {
        StatusCode int
        Headers map[string]string
        Body string
    }
}

func (tc *HttpTestCase) Pass() bool {
    fmt.Printf("✓ API:%s\n", tc.Name)
    return true
}

func (tc *HttpTestCase) Fail(reason string, expected interface{}, actual interface{}) bool {
    fmt.Printf("✘ %s: Failed because '%s'\n\tExpected: '%v'\n\tActual: '%v'\n", tc.Name, reason, expected, actual)
    return false
}

func (tc *HttpTestCase) Test(client *http.Client) bool {
    if tc.Request == nil {
        return tc.Fail("Could not parse test case", "", "")
    }

    resp, _ := client.Do(tc.Request)

    if resp.StatusCode != tc.Expected.StatusCode {
        return tc.Fail("Incorrect status code", tc.Expected.StatusCode, resp.StatusCode)
    }

    for header, expected := range tc.Expected.Headers {
        if actual := strings.ToLower(resp.Header.Get(header)); actual != expected {
            return tc.Fail("Header mismatch for " + header, expected, actual)
        }
    }

    if tc.Expected.Body != "" {
        bodyBytes, err := ioutil.ReadAll(resp.Body)
        if err != nil {
            return tc.Fail("Failed to parse body", tc.Expected.Body, "")
        }
        actualBody := strings.TrimSpace(string(bodyBytes))
        if actualBody != tc.Expected.Body {
            return tc.Fail("Body does not match", tc.Expected.Body, actualBody)
        }
    }

    return tc.Pass()
}

func parseHeaders(headers string) map[string]string {
    ret := make(map[string]string)
    for _, header_line := range strings.Split(headers, "\n") {
        header_part := strings.Split(header_line, ":")
        if len(header_part) != 2 {
            continue
        }
        ret[strings.ToLower(strings.TrimSpace(header_part[0]))] = strings.ToLower(strings.TrimSpace(header_part[1]))
    }
    return ret
}

type MatchGroup struct {
    matches []string
    re *regexp.Regexp
}

func (m *MatchGroup) Get(key string) string {
    return strings.TrimSpace(m.matches[m.re.SubexpIndex(key)])
}

func (m *MatchGroup) Match(target string) bool {
    if m.re.MatchString(target) {
        m.matches = m.re.FindStringSubmatch(target)
        return true
    } else {
        return false
    }
}

func parse_http_file(fname string) *HttpTestCase {

    file, err := ioutil.ReadFile(fname)
    if err != nil {
        log.Fatal(err)
    }

    // I just concatenated the patterns in the table above here
    // and gave the important capture groups some names with the ?P<Name> syntax
    http_file_format := regexp.MustCompile(`^(?P<Method>GET|POST|PUT|DELETE)\s+(?P<URL>[^\s]*)\s?(HTTP/1.1)?\n(?P<ReqHeader>(.*:.*\n)*)(?P<ReqBody>(.|\n)*)HTTP/1.1\s?(?P<StatusCode>[0-9]*)\s?.*\n(?P<RespHeader>(.*:.*\n)*)(?P<RespBody>(.|\n)*)`)

    // Matching and Getting
    tc := &HttpTestCase{Name: fname}
    mg := &MatchGroup{re: http_file_format}

    if mg.Match(string(file)) {
        reqBody := []byte(mg.Get("ReqBody"))
        tc.Request, _ = http.NewRequest(mg.Get("Method"), mg.Get("URL"), bytes.NewBuffer(reqBody))

        for k,v := range parseHeaders(mg.Get("ReqHeader")) {
            tc.Request.Header.Set(k,v)
        }

        tc.Expected.StatusCode, _ = strconv.Atoi(mg.Get("StatusCode"))
        tc.Expected.Headers = parseHeaders(mg.Get("RespHeader"))
        tc.Expected.Body = mg.Get("RespBody")
    }
    return tc
}

func WalkMatch(root, pattern string) ([]string, error) {
    var matches []string
    err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        if info.IsDir() {
            return nil
        }
        if matched, err := filepath.Match(pattern, filepath.Base(path)); err != nil {
            return err
        } else if matched {
            matches = append(matches, path)
        }
        return nil
    })
    if err != nil {
        return nil, err
    }
    return matches, nil
}
```
