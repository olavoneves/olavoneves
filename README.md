<div align="center">
  <img src="./assets/onvs-terminal.svg" width="100%" alt="ONVS — terminal de mercado com as estatísticas reais do GitHub de Olavo Neves: candles semanais, volume de commits, carteira de linguagens e indicadores de atividade.">
</div>

<div align="center">
  <sub>
    O painel acima <strong>não é uma imagem estática</strong>. Ele é redesenhado 3x por dia por um
    workflow do GitHub Actions que lê a minha própria atividade e a plota como um ativo de bolsa.
    <a href="#-como-esse-painel-funciona">Como funciona ↓</a>
  </sub>
</div>

---

## 🏦 Tese

Sou **Olavo Neves**, **Software Engineer** formado em Análise e Desenvolvimento de Sistemas pela **FIAP**, com especialização prática em Java Web pela **Alura**.

Trabalho com **backend em Spring Boot** e **frontend em React**, construindo APIs REST, integrações com bancos relacionais e não relacionais, e código que sobrevive ao segundo ano de produção — testes, arquitetura em camadas e CI/CD.

Venho do **mercado financeiro**, e é pra lá que essa stack está apontada. O meu diferencial não é escrever código: é **entender o que aquele código faz com o número no fim da planilha**.

---

## 📈 Carteira de projetos

> A carteira abaixo é majoritariamente **posição acadêmica** — challenges da FIAP e projetos de curso, montados para aprender arquitetura, não para escalar base de usuário. Estão aqui pelas decisões técnicas dentro deles. A posição que realmente importa está logo abaixo, em [construção](#-posição-em-construção).

| Ativo | Classe | Setor | Stack | Tese |
| :--- | :--- | :--- | :--- | :--- |
| **[HERA](https://github.com/olavoneves/hera-api_v1)** | Acadêmico | Saúde | `Java` `React` `Python` `SQL` | Automação do acompanhamento de pacientes no Hospital das Clínicas, com integração via WhatsApp. Reduziu absenteísmo em até **10%** em simulação. |
| **[Clyvo Vet](https://github.com/olavoneves/clyvo-vet_api-java)** | Acadêmico | Pet / Delivery | `Java` `Spring` `.NET` | Mesma API modelada em **dois ecossistemas** (Java e C#) — exercício deliberado de comparar arquitetura, não linguagem. |
| **[GeoSat](https://github.com/olavoneves/geosat-java)** | Acadêmico | Geoespacial | `Java` `.NET` | Estrutura de serviços para dados de satélite, também em dupla implementação. |
| **[GREEVO](https://github.com/olavoneves/Greevo)** | Acadêmico | Defesa Civil | `Java` `Node-RED` `IBM Cloud` | Gestão de abrigos e estoques em emergências, com chatbot. **-30%** no tempo de cadastro em teste. |
| **[BIOGURT](https://biogurt.vercel.app)** | Acadêmico | Alimentos | `Spring Boot` `PostgreSQL` | Plataforma do iogurte de grão-de-bico com Nutrição Santa Marcelina. **Em produção.** |
| **[Genesis Contábil](https://github.com/olavoneves/genesis-contabil)** | Pessoal | Financeiro | `Spring Boot` `PostgreSQL` `Next.js` | Controle financeiro pessoal com autenticação e relatórios. Primeiro encontro da stack com o domínio de finanças. |
| **[NutriProgress](https://github.com/olavoneves/NutriProgress)** | Pessoal | Micro-SaaS | `TypeScript` | Produto para nutricionistas acompanharem evolução de pacientes. |

---

## 🎯 Posição em construção

> **Status:** em book · ainda não listado · abertura prevista para o fim de 2026

O projeto que estou montando agora é um **sistema completo voltado ao mercado financeiro** — a convergência de tudo que estudo em paralelo neste momento. Não é mais um CRUD com tema de bolsa: a ideia é que as três frentes abaixo se encontrem no mesmo lugar.

| Frente | O que entra |
| :--- | :--- |
| **Engenharia** | Java 17, Spring Boot 3, PostgreSQL, arquitetura de microsserviços, mensageria |
| **Quantitativa** | Álgebra Linear — matrizes, decomposição e otimização aplicadas a carteiras |
| **Domínio** | Produtos financeiros — renda fixa, renda variável, derivativos, precificação |

A tese é simples: **dev que entende o produto financeiro vale mais do que dev que só implementa a regra que outra pessoa escreveu.** É por isso que estou estudando a matemática e o produto junto com a stack, e não depois dela.

---

## 🧾 Alocação técnica

Como toda carteira, a minha stack tem um núcleo que não se mexe, um satélite que gira e uma parte em acumulação.

**🟡 Core — posição estrutural**
`Java 17` · `Spring Boot 3` · `Spring Data JPA` · `Spring Security` · `Hibernate` · `PostgreSQL` · `SQL`

**🔵 Satélite — posição tática**
`React` · `Next.js` · `TypeScript` · `JavaScript ES6+` · `C# / .NET` · `Docker` · `Jenkins` · `JUnit` · `Mockito` · `Python (automação)`

**🟢 Em acumulação — aporte mensal**
`AWS` · `Kubernetes` · `Kafka` · `OAuth2 / JWT` · `Apache Camel` · `SonarQube` · `Álgebra Linear` · `Produtos Financeiros`

> A coluna **Δ** do painel mostra a alocação real: quanto de cada linguagem eu escrevi nos últimos 5 meses comparado ao meu histórico total. É a única parte deste README que eu não escolho — ela vem dos bytes dos repositórios.

---

## 📊 Teses para 2026

| Tese | Horizonte | Status |
| :--- | :--- | :--- |
| **Sistema completo para o mercado financeiro** — engenharia + quantitativa + produto | Fim de 2026 | 🔴 Posição principal |
| Álgebra Linear aplicada a otimização de carteiras | Contínuo | 🟢 Em execução |
| Produtos financeiros — renda fixa, variável e derivativos | Contínuo | 🟢 Em execução |
| Spring Security avançado — JWT e OAuth2 em produção | Curto | 🟢 Em execução |
| AWS + containers (Docker / Kubernetes) | Médio | 🟡 Montando posição |
| Microsserviços com mensageria e auth distribuída | Médio | 🟡 Montando posição |
| Portfólio novo em React + Next.js | Curto | 🟢 Em execução |

---

## ⚙️ Como esse painel funciona

Cansei de ver o mesmo perfil de GitHub repetido — os mesmos três cards, o mesmo grafo de contribuição. Então construí um.

O `assets/onvs-terminal.svg` é gerado por um script Python (só stdlib, zero dependências) que roda no GitHub Actions:

```
GitHub API + calendário de contribuições
        ↓
  índice de ritmo (ONVS)
        ↓
  candles semanais + volume + média móvel
        ↓
     SVG animado em CSS  →  commit automático
```

**O índice ONVS** é a razão entre o meu ritmo curto (média exponencial de 9 dias de contribuições) e o meu ritmo estrutural (EMA de 75 dias), comprimida por um expoente para achatar dias fora da curva:

$$\mathrm{ONVS}_t = 100 \cdot \left( \frac{\mathrm{EMA}_{9}(c_t) + k}{\mathrm{EMA}_{75}(c_t) + k} \right)^{0{,}45}$$

Leitura: **100 = trabalhando no meu próprio ritmo histórico.** Acima disso estou acelerando, abaixo estou desacelerando. Como é uma razão e não juro composto, o índice oscila de verdade em vez de despencar a cada semana parada — cada candle verde ou vermelho significa alguma coisa.

O resto vem direto da fonte: **volume** são commits por semana, a **carteira de linguagens** são bytes reais por repositório, e a **fita de cotações** no rodapé mistura linguagens com os repositórios de push mais recente.

Nada é escrito à mão. Se eu passar um mês sem commitar, o painel vai mostrar isso — e essa é justamente a graça.

```bash
# rodar localmente
python scripts/build.py --user olavoneves --out assets/onvs-terminal.svg
```

---

## ☎️ Mesa de operações

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A0F16?style=for-the-badge&logo=linkedin&logoColor=4FA8F5)](https://linkedin.com/in/olavo-neves)
[![Email](https://img.shields.io/badge/Email-0A0F16?style=for-the-badge&logo=gmail&logoColor=F05A6A)](mailto:olavo9neves@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-0A0F16?style=for-the-badge&logo=whatsapp&logoColor=22D07E)](https://wa.me/5511955502307)
[![Instagram](https://img.shields.io/badge/Instagram-0A0F16?style=for-the-badge&logo=instagram&logoColor=F2B705)](https://instagram.com/olavoneves_)

---

<div align="center">
  <sub>
    <strong>Disclaimer:</strong> rentabilidade passada não garante rentabilidade futura.
    Commit diário ajuda.
  </sub>
</div>
