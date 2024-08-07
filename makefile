COMPOSE_FILE=docker-compose.yaml
COMPOSE=docker compose -f $(COMPOSE_FILE)
CONTAINER=$(c)

up: down
	sudo mkdir -p data/db
	$(COMPOSE) build 
	$(COMPOSE) up $(CONTAINER)

build: 
	$(COMPOSE) build $(CONTAINER)

start:
	$(COMPOSE) start $(CONTAINER)

stop:
	$(COMPOSE) stop $(CONTAINER)

down:
	$(COMPOSE) down $(CONTAINER)

destroy:
	$(COMPOSE) down -v --rmi all
	sudo rm -rf data
	#sudo lsof -i :5432 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true
	#sudo lsof -i :80 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true

logs:
	$(COMPOSE) logs -f $(CONTAINER)

re: destroy up

ps:
	$(COMPOSE) ps

db-shell:
	$(COMPOSE) exec db psql -U 42student players_db 

help:
	@echo "Usage:"
	@echo "  make build [c=service]        # Build images"
	@echo "  make up [c=service]           # Start containers in detached mode"
	@echo "  make start [c=service]        # Start existing containers"
	@echo "  make down [c=service]         # Stop and remove containers"
	@echo "  make destroy				   # Stop and remove containers and volumes"
	@echo "  make stop [c=service]         # Stop containers"
	@echo "  make restart [c=service]      # Restart containers"
	@echo "  make logs [c=service]         # Tail logs of containers"
	@echo "  make ps                       # List containers"
	@echo "  make help                     # Show this help"
