   ## Lekcja DevOps
   > ### Wymagania wstępne
   > - załóz darmowe konto na gitlab.com z grupą `ISA_DEVOPS` i projektem (repozytorium) `CICD`
   > - utwórz parę kluczy `ssh-keygen -t rsa -f gitlab_isa` i umieść klucz publiczny w ustawieniach profilu (`Edit profile -> SSH keys`)
   > - utwórz nowy katalog lokalny i zainicjuj projekt
   > ```bash
   >    git init --initial-branch=main
   >    git remote add origin git@gitlab.com:isa_devops/cicd.git
   > ```
   > do agenta ssh dodaj klucz prywatny `ssh-add <PRIVATE_KEY>`; jeśli korzystasz z Windows + WSL zainstaluj wcześniej agenta `pageant` https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html 
   > włącz funkcję CICD w ustawieniach projektu `Settings -> General -> Visibility, project features, permissions -> Repository -> CI/CD` i zapisz

### Zadanie
Naszym zadaniem jest zaprojektowanie i implementacja pipeline dla przykładowej aplikacji flask z fazami:
   - faza prepare: sprawdza semantykę i weryfikuje projekt
   - faza build: buduje obraz dockerowy i umieszcza go w container registry
   - faza test: wykonuje testy i tworzy raport narzędziem `pytest`
   - faza security: skanuje obraz dockerowy pod kątem bezpieczeństwa
   - faza deploy: wdraza zbudowany obraz dockerowy na srodowisko lokalne (Kubernetes)

Po wykonaniu zadania mozna podejrzec efekt wdrozonej aplikacji za pomoca komend
```bash
   kubectl get pods -n dev # zapisujemy nazwe jednego z podow
   kubectl port-forward pod/<NAZWA_PODA> 5000:5000 -n dev
```
Aplikacja powinna byc dostępna pod adresem http://localhost:5000/api/data

   ### Dodawanie runnera
   1. Zarejestruj własny runner w gitlab: `Seetings -> CICD -> Runners -> Projet runners -> New project runner`. Dodaj tag runnera `docker-runner`. Pozostałe opcje pozostaw domyslne. Kliknij `Create Runner`. W następnym oknie skopiuj authentication token, będzie nam za chwilę potrzebny. Uwaga! Token pojawi się tylko teraz - wychodząc z tej strony nie będziemy mogli go uzyskać inaczej jak przez utworzenie nowego runnera. 
   2. Wykonaj lokalnie polecenia:
   ```bash
   $ docker run --rm -d --name gitlab-runner --network kind \
   -v <TWOJA_SCIEZKA_BEZWZGLEDNA_DO_REPO>/gitlab-local-runner/config.template.toml:/tmp/config.template.toml \
   -v /var/run/docker.sock:/var/run/docker.sock \
   gitlab/gitlab-runner:latest
   ```
   ```bash
   # wchodzimy do kontenera i rejestrujemy runner
   $ docker exec -it gitlab-runner bash
   $ gitlab-runner register \
   --template-config /tmp/config.template.toml \
   --non-interactive \
   --url "https://gitlab.com/" \
   --token "<RUNNER_TOKEN>" \
   --executor "docker" \
   --docker-image gitlab/gitlab-runner:latest \
   --description "docker-runner"
   ```


  > ### Przygotowanie środowika lokalnego
  > 1. Instalacja `kind` \
  >   https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries
  >  2. Instalacja `kubectl`\
  >     https://kubernetes.io/docs/tasks/tools/#kubectl
  >  3. Stworzenie klastra
  >     ```bash
  >     kind create cluster --name isa-cicd --config ./kind-config-multinode-ingress.yaml
  >     ```
  >  4. Upewnij się, ze workery i controlplane działają
  >     ```bash
  >     kubectl get nodes
  >     ```
  >  5. Utwórz namespace dev i prod
  >      ```bash
  >      kubectl create ns dev && kubectl create ns prod
  >       ```
  >  6. Utwórz service account i token dla usera gitlab - zapisz token na później. 
  >     ```bash
  >     kubectl create serviceaccount gitlab -n dev
  >     kubectl create token gitlab -n dev
  >     ```
  >     Uwaga - token jest wazny przez 60 minut. Po tym czasie trzeba go odnowic.
  >  7. Skonfiguruj RBAC dla usera
  >   ```bash
  >   kubectl apply -f k8s/rbac.yaml 
  >   ```
  >  8. Skonfiguruj dostęp do repozytorium obrazów dockerowych. Utwórz tokeny dostępu w `Settings -> Repository -> Deploy tokens -> Add token`. Nadaj nazwę tokenowi, zaznacz scope `read_registry`, pozostałe pola zostaw domyślne. Zapisz wygenerowany token w postaci loginu i hasła i uzyj w ponizszym poleceniu:
  >  ```bash
  >     kubectl create secret docker-registry registry-credentials --docker-server=https://registry.gitlab.com --docker-username=REGISTRY_USERNAME --docker-password=REGISTRY_PASSWORD -n NAMESPACE
  >     kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "registry-credentials"}]}'
  >  ```

   > ### Zmienne pipeline variables
   > Musimy dodać zmienną K8S_TOKEN do zmiennych pipeline, aby job `deploy` mogl uzyskac dostep do srodowiska lokalnego
   > 1. W projekcie gitlab w `Settings -> CICD -> Variables -> Add variable` dodaj nowa zmienna
   > 2. W polu `Key` podaj `K8S_TOKEN`, a w pole `Value` wklej token uzyskany w pkt. 8 przygotowania środowiska lokalnego