# How Search Works at Slack

**Domain:** enterprise search / ranking · **Source:** slack.engineering/search-at-slack

## Overview
Slack search indexes each workspace as an isolated corpus rather than one global index, then re-ranks Solr's candidate results with a learned model tuned to per-user interaction signals instead of web-search-style aggregate popularity.

## Scale
27% increase in position-1 clicks and 9% increase in searches-resulting-in-clicks after shipping ML re-ranking; measurable drop in searches-per-session (fewer repeated queries needed to find the target message).

## Architecture
- **Solr** as the indexing/retrieval layer - one corpus scoped per team/workspace, since "each Slack user has access to a unique set of documents"
- **Two-stage ranking**: Solr's built-in sort produces an initial candidate set, then an application-layer **SparkML SVM** model re-ranks by relevance
- **Ranking signals** (in order of importance): message age + Lucene match score, user affinity to the message's author, channel priority, engagement (pins/stars/reactions), and content shape (word count, line breaks, formatting)
- Permissions enforced implicitly by scoping each user's index view to documents in workspaces/channels they belong to, rather than a separate ACL-filtering pass after retrieval

## Key decisions
- Indexed per-workspace instead of one global index, because workspaces are naturally disjoint document sets - this both enforces tenant isolation for free and lets Slack throw more compute per message at ranking, since each corpus is small compared to web search.
- Rejected web-search ranking approaches (aggregate click/link signals, spam/SEO defenses) because Slack's corpus has neither the aggregate query volume nor adversarial content web search defends against - the constraints that make web ranking hard don't apply here.
- Weighted user-affinity and channel-priority signals above raw text match score, because in a closed workspace "who said it" and "where" predict relevance better than keyword frequency alone.

## Reusable patterns
- **Two-stage retrieval + re-rank**: use a cheap engine (Solr/Lucene) for initial recall, then a small learned model for precision re-ranking - cheaper than pushing all ranking logic into the search engine itself.
- **Tenant-scoped indexes as a permissions mechanism**: when data is naturally partitioned by tenant, indexing per-tenant gets you access control and smaller/faster corpora in one design choice, instead of a global index plus a filter step.
