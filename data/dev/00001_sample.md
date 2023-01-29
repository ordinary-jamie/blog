---
id: 1
title: Sample
date: 2022-01-18
preview: |
  Sample Markdown testing
section: dev
tags:
  - python
  - economics
draft: false
---

# Black-Scholes Model

The **Black–Scholes** `/ˌblæk ˈʃoʊlz/` or **Black–Scholes–Merton model** is a mathematical model for the dynamics of a financial market containing derivative investment instruments. From the parabolic partial differential equation in the model, known as the [Black–Scholes equation](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation), one can deduce the Black–Scholes formula, which gives a theoretical estimate of the price of European-style options and shows that the option has a unique price given the risk of the security and its expected return (instead replacing the security's expected return with the risk-neutral rate). The equation and model are named after economists [**Fischer Black**](https://en.wikipedia.org/wiki/Fischer_Black) and [**Myron Scholes**](https://en.wikipedia.org/wiki/Myron_Scholes); [**Robert C. Merton**](https://en.wikipedia.org/wiki/Robert_C._Merton), who first wrote an academic paper on the subject, is sometimes also credited.

## Implementation

We can implement the Black-Scholes model in Python:

``` python
import numpy as np
from scipy.stats import norm

N = norm.cdf

def BS_CALL(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * N(d1) - K * np.exp(-r*T)* N(d2)

def BS_PUT(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*N(-d2) - S*N(-d1)
```

## History
Economists Fischer Black and Myron Scholes demonstrated in 1968 that a dynamic revision of a portfolio removes the expected return of the security, thus inventing the risk neutral argument. They based their thinking on work previously done by market researchers and practitioners including Louis Bachelier, Sheen Kassouf and Edward O. Thorp. Black and Scholes then attempted to apply the formula to the markets, but incurred financial losses, due to a lack of risk management in their trades. In 1970, they decided to return to the academic environment. After three years of efforts, the formula—named in honor of them for making it public—was finally published in 1973 in an article titled "The Pricing of Options and Corporate Liabilities", in the Journal of Political Economy. Robert C. Merton was the first to publish a paper expanding the mathematical understanding of the options pricing model, and coined the term "Black–Scholes options pricing model".

### Consequences

The formula led to a boom in options trading and provided mathematical legitimacy to the activities of the Chicago Board Options Exchange and other options markets around the world.

Merton and Scholes received the 1997 Nobel Memorial Prize in Economic Sciences for their work, the committee citing their discovery of the risk neutral dynamic revision as a breakthrough that separates the option from the risk of the underlying security. Although ineligible for the prize because of his death in 1995, Black was mentioned as a contributor by the Swedish Academy.

## Typography

**This is bold text**

*This is emphasised text*

__Underlined text__

[Link to google](https://www.google.com)


## Lists

Bullet points:

- This is the first
- Second
    + Nested
    + Nested 2
- Third

Enumerated:

1. Tomatoes
2. Potatoes
3. Apples

## Tables

| Col 1 | Col 2 | Col 3   |
|-------|-------|---------|
| Row 1 | Test  | `hello` |

## Code

Some inline code `doSomething()`

Some bash code
``` bash
cd ~/Downloads
touch newFile.txt
```

Some python code

``` python
import antigravity

print("hello world")

class FrontMatter(BaseModel):
    id: int
    title: str
    date: datetime.date
    preview: str
    section: str
    tags: list[str]
    draft: bool = True

    @property
    def ref(self):
        return f"{self.section}/{self.id}"

    @validator("title", "preview")
    def normalise(cls, v):
        v = v.strip()
        v = v[0].upper() + v[1:]
        if not v.endswith("."):
            v += "."
        return v
```
