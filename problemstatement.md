# Problem Statement — Nykaa Fashion

## 1. Context — What is happening?

Nykaa Fashion has millions of users who browse, evaluate, save, and purchase fashion products. Among these behaviors, adding a product to a wishlist is a particularly valuable signal because it indicates that a user has expressed interest in a product but has not yet completed the purchase.

However, users can accumulate dozens or even hundreds of wishlisted products over time, while only a relatively small proportion are eventually purchased.

Nykaa Fashion’s strategic objective is to **increase the percentage of users who purchase at least one wishlisted product within 30 days of adding it**.

Improving this metric could increase purchase frequency, strengthen monetization from existing users, and unlock more value from demand that already exists on the platform.

---

## 2. User — Who is experiencing the problem?

The primary users are **Nykaa Fashion shoppers who save products to their wishlist but do not subsequently purchase them within 30 days**.

These users are not necessarily uninterested. In many cases, the wishlist may represent:

* A product they genuinely intend to purchase later
* A shortlist of products they are comparing
* A product they like but are uncertain about
* A product they want to revisit for a future occasion
* A temporary bookmark for inspiration or browsing

Therefore, a wishlist addition alone does not reveal the user’s underlying purchase intent, decision stage, or reason for postponement.

---

## 3. Problem — What is preventing purchase?

**The underlying reasons why users fail to convert wishlisted products into purchases are not well understood.**

After a user identifies a product they like enough to save, they may still have unresolved questions or friction around:

* Fit, size, and expected appearance
* Quality, material, or product authenticity
* Reviews and social proof
* Styling and how the product will look when worn
* Suitability for a specific occasion
* Price or perceived value
* Comparing similar products
* Waiting for a better time to purchase
* Availability, delivery, returns, or other purchase-related uncertainty
* Validation from external sources, social media, creators, friends, or other platforms

As a result, **the wishlist currently tells Nykaa Fashion what users saved, but not why they saved it, what prevents them from buying it, or what information they need to make a confident decision.**

The core problem is therefore not simply low conversion. It is the **lack of understanding of the unmet user needs and decision barriers between “I like this product” and “I am ready to buy this product.”**

---

## 4. Impact — Why does solving this matter?

Without understanding these underlying barriers, product and growth teams risk building generic interventions that address symptoms rather than the actual user problem.

This creates three challenges:

**For users:**
Users may repeatedly revisit, compare, research, or postpone purchases because important questions remain unresolved.

**For Nykaa Fashion:**
High-intent demand represented by wishlisted products may remain unrealized, limiting purchase frequency and monetization from existing users.

**For Product/Growth teams:**
Teams lack evidence-backed insights to determine which user problems should be prioritized and which product experiences could meaningfully influence the 30-day purchase outcome.

---

## 5. Constraints & Discovery Need — What must be discovered before solving it?

Before proposing a product solution, Nykaa Fashion needs to **discover and validate the underlying user problems at scale**.

An AI-powered discovery engine should analyze publicly available user conversations from sources such as:

* App Store reviews
* Play Store reviews
* YouTube comments

The system should go beyond sentiment analysis or simple review summarization. It should identify, quantify where possible, and compare the **behavioral patterns, decision barriers, unmet needs, and opportunity areas** associated with users moving from product discovery and saving to eventual purchase.

The discovery process should answer questions such as:

* Why do users add products to their wishlist?
* Which wishlisted products represent strong purchase intent versus simple bookmarking?
* What prevents users from purchasing after saving an item?
* What uncertainties remain after a product has been shortlisted?
* Why do users postpone purchase decisions?
* How do users compare multiple shortlisted products?
* What information do users seek outside Nykaa Fashion before purchasing?
* What roles do fit, size, styling, price, reviews, occasion, and social validation play?
* How do these barriers differ across meaningful user segments?
* Which unmet needs appear consistently across user conversations?
* Which opportunity areas have the strongest potential to influence the target business metric?

### Core problem statement

**Nykaa Fashion does not yet have a sufficiently evidence-backed understanding of why users who express product interest by saving items to their wishlist fail to complete a purchase within 30 days. We need to discover the specific user needs, uncertainties, decision barriers, and behavioral patterns that exist between product shortlisting and purchase, using AI-powered analysis of user feedback at scale, so that we can identify the highest-impact product opportunities—without relying on monetary incentives.**

### Key principle

**Do not start by asking “What feature should we build?”**

First determine:

**What user behavior is breaking? → Why is it happening? → For whom? → How frequently? → What unmet need explains it? → Which opportunity is most likely to improve the business outcome?**
