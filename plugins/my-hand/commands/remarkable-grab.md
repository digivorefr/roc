---
description: Capture the current page of a reMarkable 2 notebook over USB and deliver it as a multimodal image to the model. Use this command whenever the user invokes "/my-hand:remarkable-grab", says "remarkable", "rM", "remarkable grab", "capture remarkable", "grab my notebook", "read my reMarkable", "saisir remarkable", "capture reMarkable", "lire mon reMarkable", "attrape ma page", or any similar request to pull a notebook page from a reMarkable tablet plugged in via USB.
argument-hint: [notebook-name]\n[optional free-text prompt]
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/my-hand-grab:*)
  - Read
---

Run the capture binary and forward its stdout verbatim into this turn as the authoritative instruction block. The binary handles every branch (list mode, capture, errors) and always exits 0 with a well-formed prompt body.

!`"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/my-hand-grab" "$ARGUMENTS"`
