---
name: wiki
description: 規範本專案中 Gitea (完整原始碼) 與 GitHub (無內部文件) 雙遠端的 Git 同步流程。
---

# Wiki Skill (Dual Remote Git Synchronization)

本專案使用雙遠端 (Dual Remote) 策略管理原始碼與文件。

## 遠端定義
1. **Gitea (`gitea`)**: 內部完整備份。包含原始碼、`.agents` 以及所有內部文件 (如 `wiki/`, `publish/` 等)。預設分支為 `main`。
2. **GitHub (`origin` 或 `github`)**: 對外發布版本。僅包含原始碼與公開的 `README.md`。嚴禁包含 `wiki/` 以及 `publish/` 等內部開發與建置相關資料夾。

## 操作規範

當使用者要求提交程式碼或推送到遠端時，請嚴格遵循以下步驟：

### 1. 推送到 Gitea (內部預設流程)
- 確認目前位於 `main` 分支。
- 將變更加入 Git (`git add -A`) 並提交 (`git commit`)。
- 執行推送到 Gitea: `git push gitea main`。
- **Gitea 包含本專案的全部內容，沒有任何檔案限制。**

### 2. 發布到 GitHub (開 PR 或 Push)
- 由於 GitHub **不允許** 存在 `wiki/` 等文件，請透過專屬分支 `github-public` 進行發布。
- **同步流程：**
  1. 切換至 `github-public` 分支: `git checkout github-public`
  2. 從 `main` 合併最新變更，但先不提交: `git merge main --no-commit --no-ff`
  3. 若 `main` 分支有新增不應公開的資料夾，立刻將其移除: `git rm -rf --cached wiki publish .agents` 
  4. 完成合併提交。
  5. 將 `github-public` 推送到 GitHub 遠端。

> [!WARNING]
> 絕對不要將 `main` 分支直接推送到 GitHub，否則會造成內部機密/開發文件外流。
