# 🔧 Corrigir Autenticação GCP

## Problema Atual

A conta autenticada é `david.duarte@g.globo`, mas deveria ser `david.duarte@outlook.com`.

## ✅ Solução - Passo a Passo

### 1. Fazer Login com a Conta Correta

Execute no PowerShell:

```powershell
gcloud auth login
```

Isso vai:
1. Abrir o navegador automaticamente
2. Pedir para você selecionar a conta `david.duarte@outlook.com`
3. Autorizar o acesso

### 2. Definir como Conta Ativa

```powershell
gcloud config set account david.duarte@outlook.com
```

### 3. Configurar Application Default Credentials

```powershell
gcloud auth application-default login
```

Novamente:
1. Abrirá o navegador
2. Selecione `david.duarte@outlook.com`
3. Autorize

### 4. Verificar

```powershell
gcloud auth list
```

Deve mostrar:
```
ACTIVE  ACCOUNT
*       david.duarte@outlook.com
```

### 5. Testar Acesso ao Bucket

```powershell
gsutil ls gs://agrofinder/
```

Deve listar as pastas:
```
gs://agrofinder/anuncios/
gs://agrofinder/organico/
```

## 🔄 Se Precisar Alternar Entre Contas

### Listar contas disponíveis
```powershell
gcloud auth list
```

### Alternar para outra conta
```powershell
gcloud config set account CONTA@EMAIL.COM
```

### Remover uma conta
```powershell
gcloud auth revoke CONTA@EMAIL.COM
```

## ✅ Comandos Completos

Execute em sequência:

```powershell
# 1. Login com conta correta
gcloud auth login

# 2. Definir como ativa
gcloud config set account david.duarte@outlook.com

# 3. Configurar ADC
gcloud auth application-default login

# 4. Verificar
gcloud auth list

# 5. Testar
gsutil ls gs://agrofinder/
```

Após isso, execute novamente:
```powershell
.\scripts\verify_security.ps1
```

