# YouTube Engine — Ideation Research

*Research compiled 2026-07-25. Phase 1 of the YouTube engine work: understanding what
people actually want to watch, how successful channels generate ideas, and the audience
psychology that makes videos get clicked and watched. Findings feed directly into the
design of the engine's ideation pipeline.*

---

## 1. What people actually want to watch

### 1.1 The big proven categories

By raw search volume and viewership, the perennially dominant niches are **gaming,
music, entertainment, education, fitness, food/cooking, and travel**. Music,
entertainment, and education remain the most-viewed content categories platform-wide.
YouTube reaches ~2.85B users in 2026, with 25–34 year olds as the largest audience
segment and ~90% of visits coming from mobile.

High-demand content *types* (orthogonal to niche):

- **Tutorials / how-to** — step-by-step problem-solving (tech fixes, cooking
  techniques, life hacks, professional skills). Evergreen, ranks consistently in
  search, and answers an immediate need.
- **AI and technology** — anything AI-related sits in the top tier of 2026 niches;
  demand is still growing faster than supply in applied/practical sub-topics.
- **Health and wellness** — 3 in 5 adults use YouTube to learn about health topics.
  Aging populations drive wellness demand; Gen Z drives mental-health and
  mindfulness growth.
- **Faceless storytelling** — narrated/AI-assisted-visual content with high
  retention and high CPMs; notable because it's the format most compatible with an
  automated engine.

### 1.2 Underserved niches (high demand, low competition)

The common trait: real search demand where the top results are outdated, poorly
produced, or posted inconsistently. Standouts for 2026:

- **Niche hobby tutorials** — bookbinding, urban sketching, mechanical keyboards,
  aquascaping. Passionate communities, thin creator supply.
- **Applied AI tutorials for specific audiences** — e.g. AI for teachers (lesson
  planning, grading, classroom productivity). Strong search growth, few creators.
- **Specific-platform finance tutorials** — exactly how to use Robinhood, Webull,
  etc. Demand spiked with economic shifts; tutorial supply is thin.
- **Niche professional skills & senior digital literacy** — practical skill-building
  for specific jobs, and tech guidance for older users.
- **Local/regional content** — city guides, local reviews, regional events.
  Built-in audiences, almost no creators serving them.
- **Themed ambient/focus content** — urban rain, lofi city loops, guided nature
  audio. Used daily for work/sleep/study, so demand is stable and repeat-view heavy.
- **Diaspora/immigrant community content** — systematically underserved because
  creators default to majority-demographic audiences.

### 1.3 Evergreen vs. trending

- **Evergreen** content compounds: it keeps accumulating views for months/years
  (one cited example: a trending video got 50K views then flatlined at 90 days,
  while a "boring" how-to from months earlier kept growing daily).
- **Trending** content spikes then dies, but is the fastest way to get discovered
  by new viewers.
- The consensus 2026 strategy is a blend: **~60–70% evergreen core + ~30–40%
  trend overlays within the same niche**. Trends bring visibility; evergreen
  converts it into durable, compounding watch time.

**Engine implication:** the ideation pipeline should tag every candidate idea as
evergreen or trending and maintain that ratio in the output queue.

---

## 2. How successful channels ideate

### 2.1 Packaging-first (title & thumbnail before anything else)

The single most consistent pattern among top creators: **the title and thumbnail are
made first — before scripting, before filming**. If the packaging isn't irresistible,
the idea dies before any production money is spent (this is explicitly MrBeast's
rule). Benefits:

- The video is built to deliver on the promise of the packaging, not the reverse.
- Weak ideas get killed at the cheapest possible stage.
- Production gets clearer direction from day one.

Supporting practices:

- Define a one-sentence promise first: *"In this video you will learn how to ___
  so that you can ___."* If both blanks can't be filled, the idea isn't ready.
- Generate many thumbnail/title variations — the best concepts usually emerge only
  after executing a few inferior ones.
- Pair an emotionally evocative thumbnail with an equally evocative title;
  the combination drives clicks more than either alone.

### 2.2 The MrBeast-style ideation system (industrialized creativity)

- A dedicated ideation team tracks trends, tests titles, and drafts thumbnails.
- Weekly structured brainstorms: each person brings ~5 concepts; no criticism
  during initial pitches; everything recorded.
- Ideas pass through filter questions: *Would this thumbnail get clicked? Could
  this sustain 15+ minutes? Does this feel like something only we would do?*
  Most ideas die here.
- Concept work runs as a pipeline feeding production, with the calendar planned
  6–8 months out and concepts simultaneously at different stages.

**Engine implication:** this is a blueprint for automation — generate many candidates,
score them against filter questions, kill aggressively, and keep a staged pipeline.

### 2.3 Outlier analysis (the strongest data-driven ideation signal)

An **outlier** is a video that massively overperforms its channel's own baseline
(commonly measured against the trailing ~10-video median). Why it matters:

- A viral video from a 50M-sub channel says little about what will work for a small
  channel; an outlier from a 50K-sub channel that got 5M views is a **proven,
  replicable formula** independent of audience size.
- Tools in this space: 1of10, vidIQ Outliers, Spotter Studio, OutlierKit — all built
  on the same idea: find videos beating their channel's baseline, then adapt the
  format/topic/packaging.

**Engine implication:** outlier detection (views vs. channel baseline, normalized by
channel size and video age) should be a core data source for idea generation —
arguably the highest-signal input available.

### 2.4 Search demand vs. browse/suggested demand

Three traffic sources, three different content strategies:

| Source | What it is | What wins there |
|---|---|---|
| **Search** | Existing, explicit demand; highest intent | Titles that match intent literally (not teasers) and videos that pay off immediately. Evergreen foundation. |
| **Browse** (homepage) | Algorithmic top-of-funnel awareness | Broad-appeal formats on timely/widely interesting topics with high-CTR packaging. The breakout layer. |
| **Suggested** | Co-visitation ("viewers of A also watched B") | Deep, interconnected content — series and playlists within a niche. The bridge between videos. |

The best videos are designed with a chance at all three. New/small channels should
anchor on **search** (demand you can verify and capture), then build suggested
clusters, then chase browse breakouts.

---

## 3. Audience psychology — why people click and keep watching

### 3.1 Why people click: the curiosity gap

Loewenstein's **information-gap theory**: perceiving a gap between what you know and
what you want to know creates psychological discomfort; clicking is how viewers close
the gap. Effective packaging gives *just enough* information to want more but not
enough to feel satisfied without clicking:

- Before/after compositions with the "after" partially hidden
- Facial expressions of disbelief or strong emotion
- Numbers that raise questions
- Visuals that don't quite make sense without context

Emotion is the multiplier: joy, surprise, intrigue, or shock in the thumbnail,
matched by an equally evocative title.

### 3.2 What keeps people watching: open loops, stakes, closure

- **Curiosity loops** — introduce an unresolved question early; brains are
  neurologically uncomfortable with incomplete information and will keep watching
  to close the loop.
- **Micro-hooks** — periodic signals that something interesting is coming soon,
  opening new small loops before old ones close.
- **Stakes and story structure** — clear stakes, obstacles, and resolution create
  anticipation loops; the brain seeks closure.
- **Emotional salience** — content sparking curiosity, surprise, empathy, or mild
  tension is remembered longer and watched further.
- **Immediate payoff for search traffic** — a search-driven title is read as a
  literal answer, so the video must deliver fast or retention collapses.

### 3.3 The click-to-watch contract

Clicks and retention are one system, not two: packaging makes a promise, the video
keeps it. Over-promising raises CTR but destroys retention (and the algorithm
punishes the combination); the packaging-first workflow (§2.1) exists precisely to
keep the promise and the payoff aligned.

---

## 4. Implications for the YouTube engine

1. **Ideation should be packaging-first.** The engine's unit of ideation is a
   *(title, thumbnail concept, one-sentence promise)* triple — not a topic string.
2. **Score and kill aggressively.** Encode the MrBeast filter questions as scoring
   criteria; most generated ideas should die before production.
3. **Outlier detection is the highest-signal data feed.** Track channels in target
   niches, compute baseline-relative performance, and mine outliers for replicable
   formats.
4. **Tag demand type.** Every idea gets labeled search/browse/suggested-oriented and
   evergreen/trending; the output queue targets ~60–70% evergreen and anchors small
   channels on search demand.
5. **Psychology as generation constraints.** Curiosity gap in packaging, open loop
   in the first 30 seconds, stakes stated early, promise paid off — these become
   checklist items the engine validates per idea/script.

## 5. Most promising topic areas (shortlist)

Ranked by demand strength × competition gap × automation-friendliness:

1. **Applied AI tutorials for specific audiences** (teachers, seniors, specific
   professions) — high search growth, thin supply, tutorial format suits scripted
   production.
2. **Faceless storytelling / explainer content** — high retention and CPM, and the
   only category that's fully compatible with an automated engine end-to-end.
3. **Niche hobby tutorials** — passionate underserved communities; evergreen search
   demand.
4. **Specific-platform finance how-tos** — exploding demand, weak incumbent
   content; note: higher accuracy/compliance bar.
5. **Themed ambient/focus content** — stable daily-use demand, repeat views,
   near-zero scripting cost; low ceiling per video but strong as a portfolio base.
6. **Health/wellness education** — huge demand (3 in 5 adults), but crowded and
   subject to platform medical-content scrutiny; pursue narrow sub-niches only.

## 6. Sources

- [vidIQ — 80 Top YouTube Niches for High Growth in 2026](https://vidiq.com/blog/post/best-youtube-niches/)
- [Mediacube — Best YouTube Niches to Start a Channel in 2026](https://mediacube.io/en-US/blog/best-youtube-niches)
- [Lemonlight — Most Popular YouTube Niches in 2026](https://www.lemonlight.com/blog/what-are-the-most-popular-youtube-niches/)
- [OutlierKit — Top 10 YouTube Niches in 2026](https://outlierkit.com/blog/top-10-youtube-niches)
- [OutlierKit — Untapped YouTube Niches 2026](https://outlierkit.com/blog/untapped-youtube-niches)
- [Vidpros — Low Competition YouTube Niches 2026](https://vidpros.com/youtube-niches-with-low-competition/)
- [FluxNote — 15 Untapped YouTube Niches 2026](https://fluxnote.io/guides/untapped-youtube-niches-2026)
- [videotoblog — YouTube Thumbnail and Title Workflow](https://www.videotoblog.ai/resources/youtube-thumbnail-and-title-workflow-how-to-produce-more-content-with-less-stress)
- [Spotter Studio — How Pro YouTubers Optimize Titles & Thumbnails](https://www.spotterstudio.com/blog/optimize-youtube-titles-thumbnails)
- [Thomas Frank — YouTube Thumbnail Design Guide](https://thomasjfrank.com/creator/youtube-thumbnail-design-the-ultimate-guide/)
- [Digital Information World — How MrBeast Builds Viral Videos](https://www.digitalinformationworld.com/2025/08/how-mrbeast-builds-viral-videos.html)
- [TechCrunch — Former MrBeast strategist building AI ideation tool](https://techcrunch.com/2025/11/24/former-mrbeast-content-strategist-is-building-an-ai-tool-for-creator-ideation-and-analytics/)
- [OutlierKit — MrBeast Growth Strategy](https://outlierkit.com/resources/mrbeast-growth-strategy/)
- [vidIQ — Outliers feature](https://vidiq.com/features/outliers/)
- [OverseerOS — YouTube Outlier Analysis](https://www.overseeros.com/blog/youtube-outlier-analysis)
- [OverseerOS — YouTube Search Intent Strategy](https://www.overseeros.com/blog/youtube-search-intent-strategy)
- [Miraflow — YouTube Traffic Sources 2026](https://miraflow.ai/blog/youtube-traffic-sources-2026-browse-search-suggested-system)
- [ytshark — YouTube Browse Features](https://ytshark.com/youtube-browse-features-meaning/)
- [Thumbnailr — YouTube Thumbnail Psychology](https://medium.com/@BrookhamDigital/youtube-thumbnail-psychology-why-viewers-click-1bbc7fb95199)
- [JXT Group — Psychology of Audience Retention](https://www.jxtgroup.com/the-psychology-of-audience-retention-advanced-strategies-to-keep-youtube-viewers-engaged-throughout-your-videos/)
- [OverseerOS — YouTube Hook Framework](https://www.overseeros.com/blog/youtube-hook-framework-7-openings-that-keep-viewers-watching)
- [NCBI — Neurophysiologic immersion during video consumption](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9792976/)
- [Subscribr — Evergreen vs. Trending Topics](https://subscribr.ai/youtube-strategy/evergreen-vs-trending-youtube-topics)
- [TubeBuddy — Evergreen YouTube Content Strategy](https://www.tubebuddy.com/blog/evergreen-youtube-content-strategy/)
- [YouTube Culture & Trends Reports](https://www.youtube.com/trends/report/)
- [RecurPost — YouTube Statistics 2026](https://recurpost.com/blog/youtube-statistics/)
- [Global Media Insight — YouTube Statistics 2026](https://www.globalmediainsight.com/blog/youtube-users-statistics/)
