# How Apple AirTags Work

**Domain:** low-power IoT tracking / crowdsourced relay · **Source:** newsletter.systemdesign.one/p/how-do-airtags-work

## Overview
Tracks items without GPS (too power-hungry for a coin-cell tag) by broadcasting a public key over BLE and letting nearby iPhones relay encrypted location on the tag's behalf - Apple's servers never see plaintext location.

## Scale
BLE public-key broadcast every 2 seconds · Ultra Wideband for short-range precision · minimal power draw vs GPS/cellular.

## Architecture
- **Distributed location relay**: AirTag broadcasts only its public key; any nearby iPhone encrypts its own GPS + timestamp with that key and uploads it
- **End-to-end encryption**: public/private keypair set up at pairing; tag-side encrypt, owner-side decrypt only
- **Elliptic curve cryptography**: lightweight enough for a low-power passive device
- **Crowdsourced "Find My" network**: millions of Apple devices act as passive, opportunistic relays
- **Zero-knowledge server design**: Apple stores only encrypted blobs, never plaintext location
- **Digital signatures** verify relay authenticity (same idea as email sender verification)
- **Tiered comms**: BLE/UWB when owner is close, crowdsourced relay when far away

## Key decisions
- No GPS/cellular on the tag itself - battery and infrastructure cost is prohibitive for a device this small.
- Encrypt on the relaying device, before upload - Apple structurally cannot see the location, which is the actual privacy guarantee, not a policy promise.

## Reusable patterns
- **Lightweight public-key broadcast + external infrastructure for context**: any small/passive device can broadcast an identifier and let a bigger network supply location/context - applies to IoT and asset tracking generally.
- **Opportunistic data relay via nearby connected devices**: useful for sparse/offline-first networks (wildlife tracking, disconnected field sensors) where the tracked device can't maintain its own connectivity.
