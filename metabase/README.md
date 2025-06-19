# Metabase + PostgreSQL com Docker Compose

Este projeto utiliza o Docker Compose para orquestrar um ambiente com dois bancos de dados PostgreSQL e uma instância do Metabase.

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- (Opcional) Um editor de texto, como [VS Code](https://code.visualstudio.com/)
- Instale o dbeaver [Dbeaver](https://dbeaver.io/)
## Estrutura dos Serviços

- **db-metabase**: Banco de dados PostgreSQL utilizado pelo Metabase.
- **db-dw**: Banco de dados PostgreSQL adicional (Data Warehouse).
- **metabase**: Plataforma de BI Metabase conectada ao `db-metabase`.

## Como usar

1. **Configure as variáveis de ambiente**

   Edite o arquivo `.env` para definir usuários, senhas e nomes dos bancos de dados.

2. **Suba os containers**

   No terminal, execute:
   ```sh
   docker-compose up -d
   ```

3. **Acesse o Metabase**

   Abra [http://localhost:3000](http://localhost:3000) no navegador.

## Portas

- Metabase: `3000`
- db-metabase: `5432`
- db-dw: `5433`

## Volumes Persistentes

- `db_data`: Dados do banco `db-metabase`
- `dw_data`: Dados do banco `db-dw`

## Parar e remover os containers

```sh
docker-compose down
```

## Destruir todos os dados e volumes

Para remover completamente os containers, redes e volumes (todos os dados serão perdidos):

```sh
docker-compose down -v
```

---

> [!NOTE] 
> Siga as melhores práticas de segurança e não exponha suas credenciais em ambientes públicos.