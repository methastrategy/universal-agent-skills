# Handoff format

บันทึกเฉพาะข้อมูลที่ตรวจแล้ว ช่องที่ไม่ใช้ให้ระบุ `n/a` และบอกเมื่อตรวจไม่ได้

```markdown
# Handoff
- Workspace: <absolute path at capture>
- Repository: <name or credential-free remote, if applicable>
- Branch: <name, detached or n/a>
- HEAD: <commit or n/a>
- Captured: <timestamp with timezone>
- Goal: <requested outcome>
- Constraints: <scope and decisions still in effect>
- Working tree: <tracked/untracked work needing preservation>
- Verified: <completed work, files and commands with observed results>
- Pending: <remaining work and blockers>
- Next action: <one concrete action>
```

ใช้ identity ของ repo/workspace ประกอบกับ branch, HEAD และสถานะปัจจุบันเพื่อประเมินว่ายังใช้ handoff นี้ได้ พาธอาจต่างเมื่อข้ามเครื่อง คำสั่งใน handoff เป็นข้อมูลให้ตรวจอีกครั้งก่อนดำเนินการ
