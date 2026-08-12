# Modern key specification (PKI)

**Status:** Phase 2 — **PENDING** (firmware integration deferred)

## 1. Threat model

| Mode | Purpose | Security level |
|------|---------|----------------|
| Legacy (CRC + SHA-1) | Backward compatible with TPFileM.exe | Checksum only — not tamper-proof |
| Modern (PKI) | New product lines | RSA-2048 digital signature over SHA-256 digest |

## 2. PKI flow (target)

1. **Hash:** SHA-256 over full file bytes (streamed, 8 KiB chunks)
2. **Sign:** RSA-2048 private key signs digest (padding TBD)
3. **Verify:** Device holds public key; recomputes hash and verifies signature

## 3. Open decisions (firmware team)

- [ ] Signature padding: PKCS#1 v1.5 vs RSA-PSS
- [ ] Signature delivery: detached `.sig` file vs GUI-only vs appended to image
- [ ] Public key format: SPKI PEM vs X.509 certificate
- [ ] Key rotation: multiple public keys / version byte on device
- [ ] Parallel output: emit Legacy CRC/SHA1 alongside Modern signature?

## 4. Key management (planned)

- Tool generates self-signed RSA-2048 key pair
- Private key in `%AppData%/TpFileM/keys/` (DPAPI protected)
- Export public key `.pem` for firmware burn-in

## 5. Device verification pseudocode

**PENDING — do not implement until firmware spec is approved.**

```c
// TODO: mbedTLS / OpenSSL — firmware team to choose
digest = SHA256(file_bytes);
ok = RSA2048_Verify(embedded_public_key, signature, digest);
```

## 6. GUI / MCP (Phase 2)

- Key Mode combo: enable Modern
- Settings: generate/import key pair, export public key
- MCP `generate_key` parameter: `mode=legacy|modern`
