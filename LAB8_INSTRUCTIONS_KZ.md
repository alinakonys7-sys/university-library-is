# №8 лаборатория — іске қосу (№1–7 жобасының жалғасы)

1. VS Code-тан осы `library_project` папкасын ашыңыз.
2. Терминалда `python -m pip install -r requirements-lab8.txt` орындаңыз.
3. Автоматты тесттер: `python -m pytest -v` (алдыңғы 5 + №8 жаңа 15 тест).
4. Docker Desktop қосулы тұрғанда: `docker compose up -d --build`.
5. Swagger: http://localhost:8000/docs; сайт: http://localhost:8501.
6. Жүктемелік тесттерді **тек жергілікті серверде** жүргізіңіз. Locust командалары (әрқайсысын бөлек орындаңыз):

```powershell
python -m locust -f locustfile.py --headless -H http://localhost:8000 -u 5 -r 1 -t 1m --csv docs/lab8/load_5
python -m locust -f locustfile.py --headless -H http://localhost:8000 -u 20 -r 2 -t 2m --csv docs/lab8/load_20
python -m locust -f locustfile.py --headless -H http://localhost:8000 -u 50 -r 5 -t 3m --csv docs/lab8/load_50
python -m locust -f locustfile.py --headless -H http://localhost:8000 -u 100 -r 10 -t 3m --csv docs/lab8/load_100
```

7. Жаңа терминалда `docker stats` іске қосып CPU және RAM мәндерін жазып алыңыз. `Ctrl+C` арқылы тоқтатыңыз.
8. Қауіпсіздікке статикалық талдау: `python -m bandit -r app`.
9. GitHub-қа жіберу: `git add .`, `git commit -m "Add lab 8 integration load security CI tests"`, `git push origin main`. GitHub → Actions нәтижесін тексеріңіз.
10. `docs/lab8/REPORT_TEMPLATE.md` ішіндегі кестелерге **нақты** нәтижелер мен скриншоттарды қосыңыз.

ЕСКЕРТУ: бастапқы жобада PUT және аутентификация/рөл модулі жоқ. PUT орнына қолданыстағы PATCH тестіленеді. Толық тапсырма үшін рөл/авторизацияны жеке енгізу қажет; оны орындалды деп көрсетпеңіз. Жүктемелік тестті тек рұқсат етілген ортада жасаңыз.
