# ArchTrack - Architecture Decision Records Management System


# STATUS FLOW
```text
Architect
---------
proposed → under_review
rejected → proposed

Reviewer
--------
under_review → accepted
under_review → rejected

Team Admin
----------
Can perform both Architect + Reviewer transitions

Org Admin
---------
Must use override endpoint
```

```text
Decision Author
    assigns/remove reviewers

Assigned Reviewer
    submits exactly one verdict

Only assigned reviewers
    can review
```