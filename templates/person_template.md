---
title: "{PERSON_NAME}"
type: person
tags:
  - person
---

# {PERSON_NAME}

> Auto-created stub. Add details about this person here.

## Mentioned In

```dataview
LIST
FROM "Meetings" OR "Notes"
WHERE contains(file.outlinks, this.file.link)
SORT file.name ASC
```
