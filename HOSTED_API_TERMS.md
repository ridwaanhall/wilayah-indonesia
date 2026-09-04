# Hosted API Terms of Service

These are the service terms for calling the hosted API at `wilayah.rone.dev`.
They are separate from the source-code licence in [LICENSE](LICENSE), which
governs the code rather than the service.

Site-wide terms are at <https://rone.dev/terms>. Where this document is more
specific about the hosted API, it governs.

## Independence and non-affiliation

This project is independent and community-maintained. It is **not** affiliated
with, endorsed by, sponsored by, or operated by any Indonesian government body,
ministry, or agency.

It serves Indonesian administrative region data — provinces, regencies and
cities, districts, and villages — that is published publicly by the relevant
authorities. The official codes and the official register remain theirs.

## The data is a snapshot, and the map moves

Administrative boundaries and codes are not fixed. Regions are created, merged,
renamed and recoded by regulation, and a village list is only accurate as of the
day it was compiled.

This service ships a static dataset with the code. It is therefore **a snapshot,
not a live mirror of the official register**, and it will drift between updates.
For anything with legal, financial, electoral or administrative consequence,
resolve against the official source rather than this API. The maintainer accepts
no liability for decisions made on the basis of this data.

Beyond that, the data is provided as-is, with no warranty of accuracy,
completeness, or timeliness.

## No service level

This is a free public endpoint. There is no uptime commitment. Endpoints may be
rate limited, moved, or withdrawn.

Because the dataset is static and held in memory, this API has no upstream to
fail — but the host still can. Cache what you can; the data changes rarely
enough that caching aggressively costs you almost nothing.

## Acceptable use

- Do not send traffic that degrades the service for others. Automated load that
  does may be blocked without notice.
- If you need the whole dataset, take it from the repository rather than
  enumerating 83,000 villages through the API one request at a time. It is the
  same data, it is faster for you, and it costs the service nothing.

## Attribution

Attribution is requested rather than contractually required: a visible credit
linking to <https://wilayah.rone.dev> wherever you present data from this
service, and a credit to the official publisher of the underlying register.

This service does not currently return a machine-readable credit line in its
responses. If attribution should be mandatory, that field goes into the
responses first — asking people to reproduce a line the API never gave them
would be a term nobody could comply with reliably.

## Commercial use

Using the hosted endpoint commercially, beyond what the source licence and this
document already permit, is by arrangement — mostly so we know what load to
expect. Contact us.

## Corrections and takedown

If you find a record that is wrong or out of date, tell us and we will fix it.
Corrections to public reference data are worth more than most bug reports.

If you represent the data source and want something changed or removed, contact
us and it will be actioned. You do not need a lawyer to make the request and we
will not require one to act on it. We answer within three business days and say
what we did.

## Security

Report vulnerabilities to <founder@rone.dev>. Do not open a public issue for a
security problem. Scope and safe-harbour terms are at <https://rone.dev/security>.

## Contact

- Operator: PT RoneAI Teknologi Internasional (RoneAI), Boyolali Regency, Central Java, Indonesia
- Maintainer: ridwaanhall
- General and commercial enquiries: <hello@rone.dev>
- Security: <founder@rone.dev>
- Website: <https://rone.dev>
