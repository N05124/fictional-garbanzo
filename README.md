# fictional-garbanzo

a concept project for an enumeration method to store authorization credentials generated as plaintext ie. [cmd] (ssh-key)

The project is intended to reduce the number of sizable steps in storing CLI or text document credentials.
credentials that would originate as human readable JSON, text stored credentials such as from ssh keygen
or API credentials stored in easily accesable document locations in plain text 


-proposed process
python3 -m http.server <port>:<ssh-keygen [storage-args]>

starts: 127.0.0.1/keystorage/<key: private|public>/blockchain.exe
runs: blockchain.exe
validates: key-set
issues credentials

🛡️ Sentinel: Local-First Decentralized SSH CA
Sentinel is a cross-platform, local-first credential management system that replaces static SSH keys with short-lived, signed certificates. It eliminates the need for a centralized cloud-based Certificate Authority (CA) by turning your trusted devices into a distributed identity network.

🚀 The Problem
Traditional SSH management relies on TOFU (Trust On First Use) and static private keys sitting on disks for years. If a laptop is stolen, every authorized_keys file on every server must be manually updated. Centralized CA solutions solve this but introduce a single point of failure and require constant internet connectivity.

✨ The Sentinel Solution
Sentinel operates on a Decentralized Node Model. Any trusted device in your network can act as a signer, issuing cryptographic "passports" (SSH Certificates) that expire in minutes.

Zero Cloud: No third-party servers. All communication happens over mTLS or SSH on your local network.

Hardware-Rooted: Integrates with macOS Secure Enclave, Windows TPM, and FIDO2/Yubikeys to ensure private keys never leave the silicon.

Native-First: No custom agents required on the target servers; Sentinel works with standard sshd configurations.

Cross-Platform: A single Go-based binary that talks natively to the macOS Keychain, Windows DPAPI, and Linux Secret Service.

🏗️ Architecture
Sentinel uses a Request-Sign-Authenticate flow:

Identity: Each device generates a long-lived identity keypair secured by the OS keychain.

Mutual Trust: Nodes discover each other via mTLS. You "authorize" a new laptop by scanning a one-time QR code or terminal challenge.

Ephemeral Access: When you run ssh server, Sentinel requests a signature from your active CA node. You receive a certificate valid for 5 minutes.

Instant Audit: Every signature request is logged into a cryptographically hashed, append-only local ledger.

🛠️ Quick Start (Prototype)
1. Initialize the CA Node

Bash
sentinel init --mode ca
2. Register a Client

Bash
# On the new device
sentinel register --discovery-code <CODE_FROM_CA>
3. Connect to a Server (local server from instances such as python3 -m http.server 8000

Bash
# Sentinel automatically signs your key and aliases the ssh command
sentinel ssh user@production-server
🔒 Security Posture
No Private Key Transmission: Private keys are generated locally and never sent over the wire.

Short-Lived Certs: Even if a certificate is intercepted, it becomes a "dead" credential within minutes.

mTLS Communication: All node-to-node traffic is encrypted and mutually authenticated.

Tamper-Evident Logs: Local logs are linked using a Merkle-tree-inspired hash chain to prevent retroactive editing.

🗺️ Roadmap
[x] Core Go-based mTLS daemon

[x] macOS Keychain & Windows DPAPI integration

[ ] SSH-Agent protocol wrapping

[ ] TUI (Terminal User Interface) for node management

[ ] Support for Headscale/Tailscale integration

🤝 Contributing
We follow a Zero-Knowledge/Least-Privilege development philosophy. Please read our SECURITY.md before submitting PRs involving cryptographic primitives.


