# 09. Ambiente e comandos

## Ambiente da dona do projeto
Windows, PowerShell, Docker Desktop. Pasta local: `E:\Plataforma Inteligente de Análise e Inteligência de Dados`. O Claude no chat **não executa** código: ela roda e reporta.

## Subir tudo
```powershell
copy .env.example .env      # só na primeira vez
docker compose up --build   # 1º build: 3 a 10+ min
```
- Frontend http://localhost:5173 · API http://localhost:8000/docs · Health http://localhost:8000/api/v1/health
- Parar: `Ctrl+C` ou `docker compose down` (`-v` apaga volumes/banco).
- Com S3 opcional: `docker compose --profile storage up` (exige `S3_IMAGE` no `.env`).

## Testes
```powershell
cd apps/backend ; pip install -e ".[dev]" ; ruff check . ; pytest
cd apps/frontend ; npm install ; npm run typecheck ; npm run build
```

## Git (primeiro envio)
```bash
git add .
git status        # confirmar que .env NÃO aparece
git commit -m "chore: fase 0 - arquitetura e estrutura inicial"
git push origin main
```
Se pedir login: usar navegador ou Personal Access Token. Se o branch for `master`: `git branch -M main`.

## Problemas conhecidos
| Sintoma | Causa / solução |
|---|---|
| `pull access denied for minio/minio` | Imagens da MinIO removidas. Usar o compose atual (minio em profile opcional). Rodar `docker compose down -v` e subir de novo |
| Erros "No such image" de postgres/redis junto com o do MinIO | Consequência: o Compose abortou os pulls |
| Variável obrigatória faltando | Conferir `.env` (`POSTGRES_PASSWORD`, `MINIO_ROOT_PASSWORD`, `S3_IMAGE=`) |
| Banco com usuário antigo `datamind` | `docker compose down -v` (volume antigo) |
| Build lento / parece parado | Normal no primeiro `npm install`/`pip install`; esperar ~10 min antes de suspeitar |
