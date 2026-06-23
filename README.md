# 🔐 Post-Quantum Cryptographic Inventory & Risk Analysis Tool

## 📌 Overview

This project implements an automated system for **cryptographic inventory, risk analysis, and prioritization** in preparation for post-quantum cryptography (PQC) migration.

Modern cryptographic systems (RSA, ECC, Diffie–Hellman) are vulnerable to quantum attacks. This tool helps identify where cryptography is used, evaluates risk, and determines which systems should be migrated first.

---

## 🚀 Features

- ✅ Cryptographic inventory model for system analysis  
- ✅ Detection of quantum-vulnerable algorithms (RSA, ECC, DH)  
- ✅ Risk scoring based on key factors:
  - Data lifetime  
  - Mission impact  
  - Exposure  
  - Upgrade difficulty  
- ✅ Time-based quantum threat simulation  
- ✅ Automated prioritization of systems  
- ✅ Classification into risk categories (CRITICAL / HIGH / LOW)  
- ✅ Migration recommendation engine  

---

## 🧠 Problem Motivation

Post-quantum migration is **not just about replacing algorithms**—it requires understanding:

- Where cryptography is used  
- What data is being protected  
- How long the data must remain secure  
- What happens if the system fails  

This project models these factors and provides a **data-driven prioritization strategy**.

---

## 🏗️ System Model

Each system is represented as:
