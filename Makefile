.PHONY: setup start down clean

setup:
	@echo "Executando setup.sh para configurar o ambiente..."
	./setup.sh
	@echo "setup.sh concluído."

start: setup
	@echo "Iniciando serviços Docker..."
	sudo docker compose up --build --force-recreate
	@echo "Serviços Docker iniciados."

down:
	@echo "Parando serviços Docker..."
	sudo docker compose down

clean: down
	@echo "Removendo volumes Docker para uma limpeza completa..."
	sudo docker compose down -v
	@echo "Limpeza concluída."