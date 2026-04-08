---
layout: posts
title: "Living Contracts: Beyond Document-Centric Interaction with Legal Agreements"
date: 2026-04-08
author: Ziheng (Fred) Huang
---


We regularly sign legal contracts for where we live, who we work with, and the services we use. However, our interaction with legal contracts has largely been limited to document reading, an experience often complicated by extended, complex, and ambiguous legal language.

Recent advances in Language Models (LMs) have introduced new possibilities for dynamically retrieving and transforming textual information into alternative formats. While current LM technology is not yet reliable enough to fully realize these possibilities due to the high-stakes nature of legal text, *what might the emerging capabilities of LMs mean for future contract interfaces?*

In this work, we explore how contracts might move beyond static documents toward interactive systems that support users before, during, and after signing, a concept we term [**Living Contracts**](https://arxiv.org/pdf/2602.01396), which will be presented at [CHI 2026](https://chi2026.acm.org/) in Barcelona.




---

## Living Contracts: Rethinking Interaction Across the Lifecycle

We introduce **Living Contracts**, a vision for contract interfaces that go beyond static documents and instead support interaction across the full contract lifecycle before, during, and after signing.

This vision is grounded in three design concepts:

- **Contextualization:** Contextualizing contractual clauses with relevant background knowledge to aid interpretation (e.g., city ordinances). 
- **Malleable Representation:** Transforming contractual information into alternative representations that aid information tasks before, during, and after contract formation.
- **Proactivity and Awareness:** Surfacing relevant contractual information at appropriate moments and transitioning contracts from a passive record into an active participant in signers’ ongoing decisions.

Together, these concepts reframe contracts as **interactive interfaces** that educate, guide, and support decision making across the full contract lifecycle.

---

## A Case Study on Leasing Contracts

To illustrate the vision of Living Contracts, we used residential leases as a case study and created three design probes implemented as interactive interfaces that reimagine the entire renting process.


### LeaseCompare (before signing)

LeaseCompare presents a novel apartment search experience where contractual terms are proactively foregrounded, priced, and subject to competition (DC1). LeaseCompare provides Contract Flexibility Score and Contract Protection Score to summarize the flexibility and legal protection the contract offers to the tenant. Users can browse, rank, and compare apartments not only by price and amenities but by contractual clauses. 



![LeaseCompare interface screenshot](/resources/blog/livingcontract/LeaseCompare.png)


### LeaseRead (during signing)

While reading and negotiating a contract, LeaseRead explores opportunities for restructuring and contextualizing legal text. 

- *Comic and Explorable Scenarios.* LeaseRead transforms static legal text into comics and interactive scenarios (DC2). Comics ground abstract contractual clauses in hypothetical situations. On the other hand, interactive Scenarios restructure information dispersed across the contract, enabling users to interactively simulate possible outcomes.

- *Information Cards.* To contextualize legal text to aid interpretation (DC1), LeaseRead features Information Cards that educate information drawn either from external legal sources (e.g., city ordinances) or social comments.

![leaseread interface screenshot](/resources/blog/livingcontract/LeaseRead.png)

### LeaseTrack (after signing)

After a contract is signed, LeaseTrack probes the opportunities and concerns of proactively supplying contractual information (DC3). For example, this may involve offering timely reminders of obligations (e.g., move out notice) and reminding signees of their legal rights in the face of disputes.

![incidenttracker interface screenshot](/resources/blog/livingcontract/incidenttracker.png)

---

## What We Found

We conducted a three-part study with 18 participants: 
1. initial semi-structured interviews on participants’ challenges with contracts; 
2. interaction with three design probes to explore opportunities and concerns of Living Contracts;
3. a design ideation session to augment contract types other than leases.

### Challenges in Current Contract Interaction

Participants described a range of challenges that extend beyond the document itself:

- **Contracts rarely take part in decisions making.** Contracts are often only considered at the point of signing, after significant commitment. Even if contracts are avialable early, comparing across multiple contract is challenging. 
- **Extended and dense legalease.** Extended and dense legal text make it difficult to find and understand key clauses.  
- **Lack awareness of legal rights.** Many legal rights are not explicitly stated in the contract, leaving users unaware of their rights.  
- **Social and situational pressures to sign** Time pressure, power imbalance, and emotional context (e.g., excitement, stress) limit meaningful engagement with contract. 

### Opportunities of Living Contracts

Participants saw the potential in how Living Contracts could tackle these barriers:

- **Educate legal rights** In LeaseRead, Information Cards introduced legal rights in city ordinances that participants were previously unaware of and helped identify ambiguous or potentially unlawful clauses they might have otherwise overlooked. Participants felt more empowered to ask for clarification and request modifications, especially under time or social pressure.

- **Transform legal text** Alternative representations of legal text supported challenges information tasks from comparing apartments in LeaseCompare or making sense of the contract in LeaseRead with Comics and Interactive Scenarios. 

- **Proactively supply information** Proactively supplying contractual information could facilitate informed decision making before (e.g., selecting an apartment in LeaseCompare) and after signing (e.g., managing obligations or advocating for rights in LeaseTrack). 


In the design ideation session, participants extended the design concepts of Living Contracts beyond leases (e.g., insurance, surgical, and loan) and proposed additional designs, including helping people interaction with multiple contracts.

## Final Thoughts

Living Contracts invites a shift from seeing contracts as static documents to viewing them as **interactive interfaces that support ongoing interactions before, during, and after signing**. If contracts are meant to govern real-world behavior across time, then designing them as *living*, *interactive* systems may be a necessary step toward making them truly usable in practice.





