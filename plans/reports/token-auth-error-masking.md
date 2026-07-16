# `edify tokens` Reports Revoked Credentials as a Transient Network Fault

Date: 2026-07-15

Reported from `pytest-md`, where `just benchmark` and the project's documented
token-verification step (`edify tokens --model sonnet <file>`) both fail with an
error that describes the wrong fault and prescribes a useless remedy.

## Symptom

```
$ edify tokens --model sonnet README.md
Error: Models API is unreachable and cannot resolve alias 'sonnet'.
This is a transient failure. Please retry.
```

Every part of that message is wrong:

- **The API is reachable.** `curl https://api.anthropic.com/v1/models` returns a
  clean `401`, i.e. a completed HTTP round-trip.
- **It is not transient.** The condition is permanent until a human acts.
- **"Please retry" is actively harmful advice.** Retrying can never succeed.
- **The alias is a red herring.** `--model haiku|opus` and full model IDs fail
  identically; alias resolution never gets a chance to run.

The real error, surfaced by calling `client.models.list()` directly with the key
loaded by `edify.user_config.get_api_key()`:

```
AuthenticationError: 401 - authentication_error:
"OAuth access token has been revoked."
```

The OAuth token in `~/.config/edify/config.toml` under `[anthropic] api_key` was
revoked. `get_api_key()` finds it and returns it fine; `make_client()` correctly
routes it to `Anthropic(auth_token=...)` on the `sk-ant-oat` prefix. Auth then
fails at the first API call.

## Root cause

`src/edify/tokens.py:121-123`:

```python
try:
    models_response = client.models.list()
except APIError as e:
    raise ModelResolutionError(model) from e
```

`APIError` is the Anthropic SDK's **base** exception class. `AuthenticationError`
(401), `PermissionDeniedError` (403), `RateLimitError` (429) and every other API
failure are subclasses, so all of them are relabelled as
`ModelResolutionError` — whose message (`src/edify/exceptions.py:27-35`) hardcodes
the claim that the API is unreachable and the failure is transient.

Only `APIConnectionError` genuinely means "unreachable". Everything else is a
server response that arrived and said no.

## Cost

Four separate diagnostic probes to reach a one-line answer, across two agent
sessions. The message sent the first investigator down a network/credentials
path (concluding `ANTHROPIC_API_KEY` was unset — edify does not read that env var
at all) and the "transient, please retry" wording invites unbounded retrying of a
permanently failing call. Any user hitting a revoked or wrong token gets the same
misdirection.

## Suggested fix

Narrow the `except` and let auth failures say what they are. `exceptions.py`
already defines `ApiError` ("Raised when a generic Anthropic API error occurs"),
so the vocabulary exists:

```python
try:
    models_response = client.models.list()
except APIConnectionError as e:          # genuinely unreachable
    raise ModelResolutionError(model) from e
except AuthenticationError as e:         # 401 — credential is bad/revoked
    raise ApiError(
        f"Anthropic API rejected the credential in {CONFIG_FILE}: {e}. "
        "Replace [anthropic] api_key with a current token."
    ) from e
except APIError as e:                    # everything else, verbatim
    raise ApiError(f"Anthropic API error: {e}") from e
```

The point is that the message should name the actual fault and the file the user
has to edit. Worth auditing for the same `except APIError` over-catch elsewhere.

## Open question: drop the config requirement by reusing the session OAuth token?

Requested by the user. If `edify` can reuse the OAuth token of the Claude Code
session it is invoked from, the `[anthropic] api_key` config requirement could be
dropped entirely and this class of staleness disappears — a revoked token in a
config file is a problem that only exists because the token is in a config file.

The plumbing is already there: `make_client()` (`tokens.py:59-63`) branches on the
`sk-ant-oat` prefix and passes `auth_token=` rather than `api_key=`, so an OAuth
token is a first-class input today. The missing piece is *sourcing* it rather than
reading it from config.

Unresolved, and needing a decision before any implementation:

1. **Where does the session token live, and is it a stable interface?** Claude Code
   holds credentials in `~/.claude/.credentials.json`. That is an internal file,
   not a published contract — reading it couples edify to an undocumented format
   that can change without notice. (Not inspected for this report.)
2. **Is the token scoped for this?** A Claude Code OAuth token is issued for Claude
   Code. Whether it is valid for direct Messages/Models API calls from a separate
   CLI, and whether such reuse is permitted by the terms it was issued under, needs
   an actual answer rather than an assumption. If it is not permitted, this idea is
   dead regardless of feasibility.
3. **What happens outside a Claude Code session?** `edify` is a general CLI. Any
   session-token path must degrade to the config file, so the config support stays
   either way — this removes a *requirement*, not a code path.

**If the answer to (2) is no**, the resolution is simply that the user puts a
current token in `~/.config/edify/config.toml`, and the only change worth making is
the error-message fix above, so the next revocation takes one probe instead of four.
