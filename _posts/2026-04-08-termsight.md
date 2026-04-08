---
layout: posts
title: "TermSight: Making Service Contracts Approachable"
date: 2026-04-08
author: Ziheng (Fred) Huang
---

We regularly click **"Agree"** to Terms of Service (ToS) that quietly govern our data and rights, such as when purchasing a ticket online from disney, signing up for reddit, or requesting ride with Uber. Increasingly, the U.S. count considers these ToS to be enforceable contracts, placing the burden to read and understand these agreements to end users. In law, this is often refered to as **the doctorine of the "duty to read"**, where signings parties are legally responsible for reading and understanding the contract before signing. 

In reality, most people don’t fully understand the implications of signing ToS: not because they don’t care, but because modern ToS are presented in a form that's misaligned with how humans actually process information. **How might we make ToS actually approachable for consumers?** In this work, we present [**TermSight**](https://arxiv.org/pdf/2506.12332), an intelligent reading interface that offers reading guidance and support at multiple levels of ToS reading, which will be presented at [CHI 2026](https://chi2026.acm.org/) in Barcelona.

![termsight interface screenshot](/resources/blog/termsight/termsight.png)


## The Problem: Modern ToS Are Not Designed to be Read

To understand consumers' information needs and challenges around ToS contracts, we conducted a formative study with 20 participants reading real-world ToS. 

We found that when people read ToS, they are not trying to understand *everything*. Instead, they especially care about information that relate to their intended usage of the service (e.g., content consumer vs. content creator) and the distribution of power between themselves and the service provider (i.e., What are the clauses that protect me vs. take advantage to me?).

However, participants faced challenges at multiple levels of ToS Reading when trying to obtain these information:

- **Which policies should I read?** <br>Challenging to navigate nested policies and decide which policies to read out of the more than 10 policies within ToS. 

- **What information should I read within a policy?** <br>Difficult to surface and interpret relevant snippets of information from extended, visually dense, and difficult text within a policy.  

- **What are the implications of specific phrases?** <br>Challenging to interpret the meaning and implications of the original text filled with jargons and vague phrases (e.g. We collect your “information”).

- **Misleading designs further complicate reading** <br>Existing features such as policy names, section headers, and overview summaries are often vague, incomplete, and misleading.

Together, these challenges make it difficult for people to locate, interpret, and prioritize information, even if they care about information within ToS. 


## TermSight: Intelligent Reading Interface for ToS

To explore how we might address the challenges of ToS reading, we built **TermSight**, an intelligent reading interface powered by Large Language Models that augments—*rather than replaces*—reading the original legally binding text.

A key idea behind TermSight is that people have varying information needs. Rather than treating all content as equally relevant, TermSight restructures dense legal text into snippets of information, each classified along two dimensions: how **relevant** it is to the reader and how **power** is distributed (i.e., whether the clause benefits the service or the user). This allows the interface to guide reader attention toward what is more likely to matter.


![termsight powermeter screenshot](/resources/blog/termsight/termsight_powermeter.png)


TermSight offers support across all levels of contract reading:

- **When deciding which policies to read**, *Power Meters* provide an overview of each policy, helping users quickly identify the distribution of potentially relevant information within each policy. On hover, users gain access to a preview summary.
- **Within a policy**, *Summary Snippets* translate dense legal text into short, plain-language summaries that guide attention to relevant content. Users can seamlessly move between summaries and the original text by clicking the Summary Snippets and Highlight Bars.  
- **When engaging with the original text**, *Phrase Scope* explains unfamiliar or ambiguous terms and presents hypothetical scenarios to ground abstract language in real-world scenarios.  

![termsight phrasescope screenshot](/resources/blog/termsight/termsight_phrasescope.png)

Crucially, every feature is tightly coupled with the original contract. Users can always trace summaries and explanations back to the source text, preserving legal fidelity while improving navigation and interpretation.


## What We Found
We conducted a within-subject study with 20 participants where each participant used both TermSight and a baseline interface to read two services’ ToS, once with each interface variant. 

- **Easier to Read**: We found that reading ToS with TermSight to *require significantly less effort*. 
- **Easier to Navigate**: When navigating ToS, *deciding which policy to read and what text to read within a policy was significantly easier* with TermSight.
- **More willing to read ToS**: Moreover, participants were *significantly more willing to read ToS* and *spend more time reading ToS* with TermSight. 

By looking at participants' interaction patterns, we also observed that participants used AI-generated summaries not as replacements, but as **entry points and verification tools** for engaging with the original text.



## Final Thoughts:

We regularly sign legal contracts for where we live, who we work with, and how we interact with digital services. Yet, these contracts have drifted from their premise of facilitating mutual understanding to complex documents that discourage reading. Our formative study revealed ineffective and deceptive designs at all levels of a ToS. 

To make service contracts approachable, we designed and evaluated an intelligent reading interface: TermSight. TermSight enabled participants the ability to surface and approach relevant information at all levels of contract reading. Taken together, TermSight presents one avenue for making legal contracts more approachable to the general public.


