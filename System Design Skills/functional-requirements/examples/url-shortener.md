# Worked example: Functional Requirements — TeamLink URL Shortener

Product idea given: "A tool for small teams to shorten URLs and see click
analytics."

## The .md document

```markdown
# Functional Requirements Document

## Document Metadata

Document ID: FRD-TEAMLINK-001
Product: TeamLink URL Shortener
Version: 1.0
Created: 2026-01-15
Status: READY_FOR_NFR

## Product Overview
TeamLink lets small teams create shortened URLs for links they share
externally, and see how those links are performing.

## Problem Statement
Teams currently share raw long URLs with no way to track engagement or
present a clean, branded link.

## Goals
- Let team members create and share shortened links quickly.
- Give teams visibility into how their links perform.

## Actors / Personas
- Team member — authenticated user who creates and views links.
- Team admin — a team member with permission to manage team membership
  and view all team links.
- Link visitor — the person who clicks a shortened link; not
  authenticated, but their click is recorded.

## Scope

### In Scope
Link creation, redirection, click analytics, team membership management.

### Out of Scope
Billing/subscription management; custom domains.

## Domain Entities
Team, Member, Link, ClickEvent

## Functional Requirements

### Link Creation

#### FR-001
Name: Create shortened URL
Actor: Team member
Priority: P0
Description: The system must allow an authenticated team member to
  create a shortened URL from a long URL.
Preconditions: User is authenticated and belongs to a team.
Trigger: User submits a long URL.
Main Flow: User submits long URL -> system generates short code ->
  system returns shortened URL.
Alternative Flows: User supplies a custom short code (see FR-002).
Failure Behavior: Invalid long URL format is rejected with an error.
Business Rules: Short codes are unique within a team.
Dependencies: None.

#### FR-002
Name: Custom short code
Actor: Team member
Priority: P1
Description: The system must allow a team member to optionally choose a
  custom short code for their link.
Preconditions: FR-001 preconditions.
Trigger: User specifies a custom code during creation.
Main Flow: User provides code -> system checks uniqueness -> link created.
Alternative Flows: None.
Failure Behavior: Duplicate code within the team is rejected (FR-003).
Business Rules: Codes are case-sensitive, alphanumeric, 3-20 characters.
Dependencies: FR-001.

#### FR-003
Name: Reject duplicate custom code
Actor: System
Priority: P0
Description: The system must reject a custom short code already in use
  within the team.
Preconditions: A custom code is supplied.
Trigger: Code collision detected.
Main Flow: N/A (validation rule).
Alternative Flows: None.
Failure Behavior: Returns a clear conflict error naming the taken code.
Business Rules: Uniqueness is scoped per team, not global.
Dependencies: FR-002.

### Link Resolution

#### FR-004
Name: Redirect to original URL
Actor: Link visitor
Priority: P0
Description: The system must redirect a visitor who follows a shortened
  URL to the original long URL.
Preconditions: The short code exists.
Trigger: Visitor requests the short URL.
Main Flow: Lookup code -> redirect (HTTP 302) to original URL.
Alternative Flows: None.
Failure Behavior: Unknown code returns a 404-style not-found response.
Business Rules: None.
Dependencies: FR-001.

#### FR-005
Name: Record click event
Actor: System
Priority: P0
Description: The system must record a click event each time a shortened
  URL is followed.
Preconditions: FR-004 redirect occurs.
Trigger: Successful redirect.
Main Flow: Record timestamp and any available referrer/location signal.
Alternative Flows: None.
Failure Behavior: A failure to record a click must not block the redirect
  itself (see NFR derivation).
Business Rules: None.
Dependencies: FR-004.

### Analytics

#### FR-006
Name: View own link analytics
Actor: Team member
Priority: P1
Description: The system must allow a team member to view click counts
  over time for links they created.
Preconditions: Member is authenticated.
Trigger: Member opens a link's analytics view.
Main Flow: Query click events for the link -> display counts over time.
Alternative Flows: None.
Failure Behavior: No data yet shows an empty state, not an error.
Business Rules: A member sees only their own links unless they are an
  admin (see FR-007).
Dependencies: FR-005.

#### FR-007
Name: View team-wide link analytics
Actor: Team admin
Priority: P1
Description: The system must allow a team admin to view click counts for
  any link created by any member of their team.
Preconditions: Actor has admin role.
Trigger: Admin opens team analytics view.
Main Flow: Query click events across all team links.
Alternative Flows: None.
Failure Behavior: Non-admin attempting this sees an authorization error.
Business Rules: Scoped to the admin's own team only.
Dependencies: FR-005, FR-006.

### Team Management

#### FR-008
Name: Invite team member
Actor: Team admin
Priority: P1
Description: The system must allow a team admin to invite a new member
  to the team.
Preconditions: Actor has admin role.
Trigger: Admin submits an invite.
Main Flow: Invite created -> notification sent to invitee.
Alternative Flows: None.
Failure Behavior: Inviting an existing member is a no-op with a message.
Business Rules: None.
Dependencies: None.

#### FR-009
Name: Remove team member
Actor: Team admin
Priority: P1
Description: The system must allow a team admin to remove a member from
  the team.
Preconditions: Actor has admin role.
Trigger: Admin removes a member.
Main Flow: Member's access is revoked.
Alternative Flows: None.
Failure Behavior: None.
Business Rules: See Open Questions re: what happens to that member's links.
Dependencies: None.

## Entity Lifecycle Requirements
A Link is Active from creation until explicitly not covered — no deletion
or expiry flow was implied by the idea (see Open Questions).

## Authorization Requirements
Team-scoped isolation: a member must never see another team's links or
click data (drives FR-006/FR-007 business rules).

## Validation Requirements
Long URL must be a well-formed URL; custom codes are alphanumeric,
3-20 characters.

## Error Handling Requirements
Redirect failures (unknown code) and creation failures (duplicate code,
invalid URL) must return distinguishable, actionable errors.

## Integration Requirements
None implied by the idea.

## Notification Requirements
Team invitations trigger a notification to the invitee (FR-008).

## Search / Reporting Requirements
Click-count-over-time views (FR-006, FR-007) are the only reporting
implied.

## Functional Edge Cases
- A link visitor clicking a code for a link whose creator was later
  removed from the team (see Open Questions).

## Functional Assumptions
- Links do not expire unless a future requirement says otherwise.

## Open Questions
- Should a removed team member's previously created links remain active?
- Is there a limit on link lifetime, or do links persist indefinitely?

## Functional Requirements Traceability

| ID | Capability | Actor | Priority | Status |
|----|------------|-------|----------|--------|
| FR-001 | Link Creation | Team member | P0 | Approved |
| FR-002 | Link Creation | Team member | P1 | Approved |
| FR-003 | Link Creation | System | P0 | Approved |
| FR-004 | Link Resolution | Link visitor | P0 | Approved |
| FR-005 | Link Resolution | System | P0 | Approved |
| FR-006 | Analytics | Team member | P1 | Approved |
| FR-007 | Analytics | Team admin | P1 | Approved |
| FR-008 | Team Management | Team admin | P1 | Approved |
| FR-009 | Team Management | Team admin | P1 | Approved |

## Completeness Assessment

Functional requirements status:
READY_FOR_NFR
```

## The matching data.json

This is what makes the document a contract rather than just prose — a
downstream skill reads this structured file rather than re-parsing the
markdown:

```json
{
  "document_id": "FRD-TEAMLINK-001",
  "product": "TeamLink URL Shortener",
  "version": "1.0",
  "created": "2026-01-15",
  "status": "READY_FOR_NFR",
  "blocking_issues": [],
  "actors": ["Team member", "Team admin", "Link visitor"],
  "domain_entities": ["Team", "Member", "Link", "ClickEvent"],
  "requirements": [
    {
      "id": "FR-001",
      "capability": "Link Creation",
      "name": "Create shortened URL",
      "actor": "Team member",
      "priority": "P0",
      "description": "The system must allow an authenticated team member to create a shortened URL from a long URL.",
      "status": "Approved",
      "dependencies": []
    }
  ],
  "open_questions": [
    "Should a removed team member's previously created links remain active?",
    "Is there a limit on link lifetime, or do links persist indefinitely?"
  ],
  "traceability": [
    {"id": "FR-001", "capability": "Link Creation", "actor": "Team member", "priority": "P0", "status": "Approved"}
  ]
}
```

(shortened here for readability — a real data.json includes every
requirement and traceability row, not just the first).

Notice what's absent from the FR content itself: no database choice, no
API Gateway, no analytics pipeline technology. Every requirement is an
observable, independently testable capability. That discipline is what
lets architecture-design make real decisions later instead of rubber-
stamping choices this document already made.
