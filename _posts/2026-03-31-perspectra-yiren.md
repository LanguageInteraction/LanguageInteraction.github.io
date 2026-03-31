---
layout: posts
title: "Re-Designing Persona-Driven Deep Research System to Encourage User Critical Thinking"
date: 2026-03-31
author: Yiren Liu
---
Research studies have been increasingly arguing for concerns over [reducing critical thinking skills](https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/) in knowledge workers. 
In the context of scientific research, the use of deep research systems for tasks like literature review and research ideation are also becoming increasingly common, thus posing similar concerns for reduced researchers' critical thinking, especially junior researchers.

What if brainstorming a new research idea felt less like interrogating a chatbot and more like moderating a panel of opinionated experts — ones you get to pick? 
That's the rationale behind [**Perspectra**](https://arxiv.org/abs/2509.20553), our new system for AI-assisted research ideation, presented at [CHI 2026](https://chi2026.acm.org/) in Barcelona.

![Perspectra interface screenshot](/resources/blog/perspectra-interface.png)


## The Problem: Chat Interfaces Aren't Built for Deep Thinking

LLM-based tools like ChatGPT and Claude have become go-to assistants for exploring new research directions. But the standard chat interface has limitations when it comes to complex knowledge tasks such as interdisplinary research ideation. You can ask a question and get an answer, but it's hard to evaluate information from multiple perspectives, track how an argument evolved, or steer a discussion toward the specific sub-topic you care about. In most cases, users tend to passively consume AI-generated content rather than actively reason through it.

We wanted to ask: **can we design multi-agent interactions that actually encourage researchers to think more critically?**

## Perspectra: A Forum for AI Expert Deliberation

Perspectra reimagines multi-agent interaction as a **threaded, forum-style discussion** among LLM-simulated domain experts. Instead of chatting with a single AI in a linear stream, users observe and participate in structured deliberation across parallel threads — each dedicated to a specific sub-topic of their research idea.

The system offers several key interaction mechanisms:

- **@-mention and reply**: Users can tag specific expert agents into a conversation, forming ad-hoc panels on the fly.
- **Thread branching**: When an interesting sub-topic emerges, users can spin off a new discussion thread to explore it in depth without losing track of the original conversation.
- **What-if panels**: Users can preview how a particular agent might respond with a specific stance (agree, disagree, question) before committing to a direction.
- **Mind map visualization**: A dynamic, semantically zoomable graph maps out the structure of the deliberation, also showing which agents made claims, who supported or rebutted whom, and why.

Each agent's response is tagged with a deliberation act (ISSUE, CLAIM, SUPPORT, REBUT, QUESTION) drawn from argumentation theory, making the reasoning structure visible and navigable rather than buried in a wall of text.


## What We Found

We ran a within-subjects study with 18 participants, comparing Perspectra against a standard multi-agent group chat. Each participant used both systems to develop **a short research proposal** on an interdisciplinary topic.


**Better proposal quality.** LLM-based and self-assessed evaluations both showed improvements in Clarity and Feasibility for proposals developed with Perspectra.

**More critical thinking activities.** Perspectra elicited significantly more higher-order cognitive activities across categories including Application, Analysis, Inference, and Evaluation compared to the group chat baseline.

**More structured revisions.** Participants using Perspectra revised their proposals significantly more often, with particularly large gains in the Motivation section. In the chat condition, users were more likely to copy-paste agent outputs; in Perspectra, they synthesized and rewrote.

## Final Thoughts

A growing concern in the HCI and AI communities is that generative AI tools may actually *reduce* critical thinking by making it too easy to offload reasoning. Perspectra takes a different approach: it introduces **productive friction**, where the @-mention and reply mechanisms require users to decide *which* experts to engage and *what* to ask, which in turn nudges them toward more deliberate reasoning. Isn't this cool? But more discussions are needed for other potential design options to better incorporate friction that encourages deep thinking without discouraging users.

We also observed emergent behaviors we didn't design for. Some participants left "TODO" anchors in their notes as self-assigned verification checkpoints. Others decomposed broad research questions into targeted sub-queries directed at specific agents. 

## Try It Out

Perspectra is open-source. You can find the code and documentation on our [GitHub repository](https://github.com/yiren-liu/Perspectra).

## Cite us!

**Perspectra: Choosing Your Experts Enhances Critical Thinking in Multi-Agent Research Ideation**
Yiren Liu, Viraj Nischal Shah, Sangho Suh, Pao Siangliulue, Tal August, and Yun Huang
*CHI 2026 · Barcelona, Spain · April 13–17, 2026*
DOI: [10.1145/3772318.3791560](https://doi.org/10.1145/3772318.3791560)
