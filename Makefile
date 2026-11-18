.PHONY: setup health ui run juger juger-strict prompt-systeme prompt-exemples test clean

setup:          ## Démarrer MLflow + RustFS (Docker) et attendre qu'ils soient prêts
	docker compose -f ../docker-compose.yml up -d
	@echo "Attente de MLflow (1re fois : quelques minutes, le temps d'installer boto3)..."
	@for i in $$(seq 1 60); do curl -sf http://localhost:5000/health >/dev/null && echo "MLflow est prêt : http://localhost:5000" && break; sleep 5; done
	docker compose -f ../docker-compose.yml ps -a

health:         ## État des services (-a : affiche aussi rustfs-setup, terminé)
	docker compose -f ../docker-compose.yml ps -a

ui:             ## Rappel des URLs
	@echo "MLflow : http://localhost:5000  (mode Model training)"
	@echo "RustFS : http://localhost:9001  (rustfsadmin / rustfsadmin)"

run:            ## RÉGLER : entraîner + mesurer sur la VALIDATION (ne lit pas le test)
	uv run python main.py

juger:          ## JUGER : porte de qualité sur le TEST (meilleur run selon la validation)
	uv run python juger.py

juger-strict:   ## Porte BLOQUANTE : un FAIL arrête en erreur
	EVAL_GATE_STRICT=true uv run python juger.py

prompt-systeme: ## Labo : modèle de base + prompt d'origine, sur la VALIDATION
	uv run python prompt_lab.py prompts/systeme.txt validation

prompt-exemples: ## Labo : prompt enrichi d'exemples du TRAIN, sur la VALIDATION
	uv run python prompt_lab.py --construire exemples-train
	uv run python prompt_lab.py prompts/exemples_train.txt validation

test:           ## Tests unitaires (données, score)
	uv run --with pytest pytest -q

clean:          ## Tout arrêter (les runs sont conservés)
	docker compose -f ../docker-compose.yml down
