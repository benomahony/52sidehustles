# Week 01: Sweet Annual Planner

## Overview

- **Category**: Print on demand
- **Skills Required**: Design, Etsy, Shopify
- **Initial Investment**: £12
- **Time Commitment**: 4 hours

## How To

This first side hustle scratched our own itch of having a annual planner that also incorporated goals, for the year and also monthly.
A quick google and we found gelato.com who do print to order, integrate with Etsy (and Shopify, etc.) and also have a pretty decent api which I could use for extensions.

For the first iteration we want the absolute minimum required to be able to sell and fulfil an order which requires the following steps:

1. Design annual planner
2. Upload to Gelato
3. Setup Etsy & Shopify store

Now I am crap with design tools and I already had it in my mind that I wanted to create my own app/landing page for this for customisation so I immediately asked Claude and ChatGPT how I could create this.

They both suggested `reportlab` as a way to programmatically create the pdfs required by Gelato but both completely buggered up the formatting requiring some odd tweaks to make sure the pdf looked nice.

Already we have an annoying iterative workflow so I thought I could use `watchfiles` to re-run the pdf generation on every save!

```python

from watchfiles import run_process


def rebuild():
    import subprocess

    subprocess.run(["python", "sidehustles/01_calendar_goals/main.py"])
    print("Reloading pdf")


if __name__ == "__main__":
    run_process("sidehustles/01_calendar_goals/main.py", target=rebuild)

```

Voilla! A much tighter iteration cycle out of the box! Similar to my experience in `mkdocs` using `mkdocs serve`

![PDF Dev Workflow](/assets/pdf_dev_workflow.png)
I quickly got the formatting to where I wanted and uploaded the pdf to gelato.com, selecting the A3 matte poster so it can be written on.

I definitely have some UX feedback for Gelato, Etsy and Shopify - It should be way easier to get started with these tools.

Gelato kept recommending new products rather than the templates I had, also I think templates isn't the best name. Ideally I'd have products for my store but I had to create a template then turn it into a product.

This wasn't that intuitive but I got going and started creating the stores. Etsy was £12 and the on boarding was quite a faff, I guess this is useful to avoid spam stores etc. but i feel there is a nicer middleground.

Shopify was free for 3 days then £1 for the first month so relatively cheap.

Check out the [Etsy store](https://www.etsy.com/shop/SweetAnnualPlanner?ref=dashboard-header) here.

And the [Shopify store](https://3y80v2-a3.myshopify.com/) here!

So now I have the complete loop working I have two options:

1. Create customisation and tracking with python?
2. Look into adverts?

Obviously 1 is more appealing to the dev but 2 looks like it might be the more useful for generating cash. What do you think I should do?

## Week's Progress

- Day 1:
- Day 2:
- Day 3:
- [...]

## Results

- Revenue: $X
- Expenses: $X
- Time Invested: X hours
- Key Learnings:
  - Learning 1
  - Learning 2

## Evaluation

[Complete evaluation using framework]

## Decision

- [ ] Continue
- [ ] Optimize
- [ ] Deprecate

## Resources

### Relevant links

- [Gelato](www.gelato.com): Print on demand
- [Shopify](www.Shopify.com): Online storefront
- [Etsy](www.etsy.com): Online storefront / makers marketplace

### Tools used

- [`reportlab`](https://docs.reportlab.com/reportlab/userguide/ch1_intro/): Create PDFs using python
- [`watchfiles`](https://watchfiles.helpmanual.io/): Code reloading on save

### Additional reading
