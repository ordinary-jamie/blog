---
id: 8
title: Teaching Python
date: 2022-11-04
preview: |
  An early introduction to objects for a Python beginner tutorial
section: dev
tags:
  - python
draft: false
type: blog
---

I've recently been ask to teach Python to an audience with no experience in Software Development!

For this, I prepared some material to project onto a screen whilst teaching. You can find it here [jamphan.dev/pytute](https://jamphan.dev/tutorial/py).

I've actually been asked to teach Python to numerous of my close (and patient) friends -- and through these experiences I've always awkwardly danced around the object-orientation (OOP) aspects of Python. OOP is a fairly abstract concept and for people who haven't even touched a command-line interface (CLI) before, it can be impossibly daunting.

But this avoidance becomes awkward and difficult quite early in the tutorials. So much of Python's high-level *verbosity* and ease-of-use is baked into its various types and their methods, and the alternative imperative work-arounds feel like tedious anachronisms.

## How objects are confusing for beginners

One of the first OOP concepts you'll quickly find yourself running into when teaching Python is string methods. Think for example the simple `"Hello, world!".upper()`

Simple for Python developers, but for beginners, there's a lot here to confuse them:

1. <span style="color: #9013fe">**New (easy to confuse with function calls) syntax**</span>: We've introduced a new syntax of `<object>.<method>()`; you may of not even talked about functions yet, and even if you had, you're now introducing an entirely (but similar) different way of calling a *method*.
2. <span style="color: #9013fe">**Object instances**</span>: We're creating a string object with the string literal, and immediately calling a method on that object. Realistically, in your tutorial, you'll probably assign the literal to a variable, and call the method from that named reference; but in either case, we have to deal with the complex topic of object *instances*.
3. <span style="color: #9013fe">**Side-effect and returns**</span>: Strings are immutable, and students can easily confuse side-effects with returns. In this case they won't see any feedback of the `upper` method as we don't capture or print out the return anywhere, but yet students may misconstrue this snippet to believe it has an inline side-effect on the object (like `list.sort`) as the code is presented in such a fashion.<br><br>A common teaching method I use is to "read the code aloud", and this can easily be miscommunicated by saying something like *"we're making a string and <span style="color: red;">turning it into</span> upper case with the upper method"* -- We're not "turning it into" anything, we're creating and returning a new string literal!

Now, the imperative case is fairly tedious. First of all, there is no built-in `toupper` function like there is in C's standard library. And, just like in C, we would first have to cover the concept of sequences (strings as character arrays), which in turn requires understanding of `for`-loops; this isn't a great alternative!

### The lesson plan for an early introduction to objects (types)

So, introducing objects may not be as avoidable as we thought. I still work around the fundamental concepts of OOP, and instead focus on types.
This is actually quite convenient since data-types is quite a necessary learning chapter for all students. However, what I do differently is to really emphasise and stay on the topic of types as opposed to glossing over them as do other tutorials.

Ultimately, I try to frame the tutorial around types

The initial schedule becomes:

1. <span style="color: #9013fe">**Basic ("primitive") data types**</span>: par for the course. This is standard in almost every programming language's 101 course.
2. <span style="color: #9013fe">**Operators**</span>. Typically this is glossed over in tutorials, instead I highlight and emphasize these to introduce to students type-specific behaviours, e.g. `+` for integers is addition, whilst `+` for strings is concatenation.<br><br>The goal is to implicitly familiarize students with the the idea of classes, and help them recognise that the "types" in data-types is more than just different representations of information. I.e. strings aren't just a different type to integers because they store text as opposed to numbers; they're different types which also **behave** differently.

3. <span style="color: #9013fe">**Calling Methods**</span>. This is quite early to be learning methods! However, here, we are just showing students that (a) they exist, and (b) how to use them. We **ignore the implementation details of methods**. This is best done by **contrasting** them against the built-in functions. In particular;

    - Highlight the syntactical difference; methods require an object, whilst functions do not.
    - In the same spirit as above, show that methods cannot be called if you do not have the **correct type**.
    - Emphasize the **why**; why is `.upper()` a method and not a built-in function? Because it doesn't make sense to have a "generic" built-in function that only applies to the string type.

And that is as far as I take OOP concepts in my tutorial! I don't even mention the word "class", and instead, entirely focus the OOP concept around typing.

## Reframing their learning journey

This is actually a fairly useful concept to have with the students, because it helps frame their learning journey going forward; Once you have the fundamental statement syntaxes (variable assignments, expressions, control structures), <span style="color: #9013fe">*the majority of your learning journey is to discover, and learn about new types. With each new type, you unlock new features and capabilities.*</span>

These can be simple types like `boolean`, or `list`, to more complicated types like `pathlib.Path`. Whatever the type, the treatment for a prospective student is the same;

- <span style="color: #9013fe">**Recognise the type is a different representation of information**</span>: strings store text, integers numbers, booleans true/false, and `pathlib.Path` stores the location of file objects.
- <span style="color: #9013fe">**Recognise each type has unique behaviours**</span>: `/` is division for integers, but it is path-joining for `pathlib.Path`
- <span style="color: #9013fe">**Recognise that each type has its own set of methods**</span>: `.upper()` is for strings, and `.exists()` is for `pathlib.Path`

I think this becomes a great way for students to compartmentalize their learnings. Nothing highlights this better, than the ability to tabulate their learnings by type. For example, in my File I/O recap, I have this table:

![](/blog/8/recap.png)

## Final comments

My tutorial, and my teaching methods are a constant work-in-progress, but with each attempt I've learnt new ways of helping students learn Python. In this case, I've realised that objects don't have to be as scary as I make them out to be (especially if you ignore the whole class creation process).

Of course, there's a lot more to flesh out in a tutorial - for example, object instances and named references can be quite confusing for beginners! I actually step them through a debugger to show how Python's symbol table grow as we progress through a routine, and from there highlight how each named reference in the symbol table is just an object instance. But that's for another blog post.