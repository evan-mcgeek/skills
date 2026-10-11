# How Twitter's Timeline Works (frontend)

**Domain:** client-side feed architecture · **Source:** newsletter.systemdesign.one/p/system-design-interview-twitter

## Overview
Unusual among these case studies: this is a *frontend* system design, not backend infra. Focuses on how a client-side SPA renders and manages a huge, constantly-updating feed.

## Architecture
- **Layered client architecture**: View (React/Vue/Svelte) → Store (Redux/Zustand) → Data access (RTK Query/Tanstack Query) → server APIs
- **SPA with client-side rendering**: persistent store survives navigation, so opening a tweet from the timeline needs no refetch
- **Normalized data store**: tweets/users/timelines held as separate entities keyed by ID, referenced not duplicated
- **Cursor-based pagination** (tweet ID as boundary) - handles a feed that's inserting/deleting in real time without duplicate or skipped items
- **Virtualized lists**: only viewport-visible tweets render; off-screen DOM nodes recycled
- **Optimistic updates**: likes/retweets reflect instantly, reconciled with server response after
- **Code splitting**: lazy-load JS per tweet type/route/interaction to shrink the initial bundle

## Key decisions
- CSR over SSR: personalized timelines get little SEO benefit from SSR, so the added complexity isn't worth it here.
- Cursor pagination over offset: naturally tolerant of items being inserted/removed mid-scroll, which offset pagination is not.

## Reusable patterns
- **Data normalization**: any product with entities shared across multiple views (dashboards, e-commerce) should store by ID reference, not duplicate objects per view.
- **Virtualization + lazy media loading**: reusable for any long feed/list/grid - combine with IntersectionObserver and progressive image decode (LQIP) for perceived speed.
