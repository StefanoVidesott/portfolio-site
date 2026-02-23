from app.database import SessionLocal
from app.models import Project, Experience, Education, SkillCategory, Language, Interest

def seed_data():
    db = SessionLocal()

    projects_data = [
        {
            "slug": "air-force-1943",
            "title_it": "Air Force 1943",
            "title_en": "Air Force 1943",
            "description_it": "Ho partecipato allo sviluppo di Air Force 1943 all'età di 15 anni durante il liceo.",
            "description_en": "I participated in the development of Air Force 1943 at the age of 15 while in high school.",
            "link_it": "Visualizza su itch.io",
            "link_en": "View on itch.io",
            "image_url": "/static/images/project-air_force_1943.webp",
            "url": "https://weatherlight.itch.io/airforce-1943",
            "is_featured": True,
            "order": 1
        },
        {
            "slug": "unitn-p2-configuration",
            "title_it": "Unitn P2 Configuration",
            "title_en": "Unitn P2 Configuration",
            "description_it": "Ho creato uno script per automatizzare l'installazione dell'ambiente di laboratorio per il corso P2 all'Università di Trento. Adottato ufficialmente dal docente e inserito nei materiali del corso.",
            "description_en": "I created a script for automating the installation of the lab environment for the P2 course at the University of Trento. Officially adopted by the professor and included in the course materials.",
            "link_it": "Visualizza su GitHub",
            "link_en": "View on GitHub",
            "image_url": "/static/images/project-unitn-p2-configuration.webp",
            "url": "https://github.com/StefanoVidesott/unitn-p2-configuration",
            "is_featured": True,
            "order": 2
        },
        {
            "slug": "wannawork",
            "title_it": "WannaWork",
            "title_en": "WannaWork",
            "description_it": "Piattaforma di job matching locale per studenti e imprese (Progetto di Ingegneria del Software).",
            "description_en": "Local job matching platform for students and businesses (Software Engineering Project).",
            "link_it": "Scopri di più",
            "link_en": "Read more",
            "image_url": "/static/images/project-wannawork.webp",
            "is_featured": True,
            "order": 3
        }
    ]

    experiences_data = [
        {
            "title_it": "Programmatore",
            "title_en": "Software Developer",
            "company": "Airpim SRL",
            "date_it": "Maggio 2024 - Maggio 2025",
            "date_en": "May 2024 - May 2025",
            "location": "Rovereto, TN",
            "tasks_it": [
                "Sviluppo e manutenzione di applicazioni web e API backend.",
                "Tecnologie: Python, Flask, SQLAlchemy, MySQL, Docker.",
                "Implementazione di sistemi di visualizzazione e manipolazione di dati.",
                "Collaborazione con il team per migliorare l'architettura software."
            ],
            "tasks_en": [
                "Development and maintenance of web applications and backend APIs.",
                "Technologies: Python, Flask, SQLAlchemy, MySQL, Docker.",
                "Implementation of data visualization and manipulation systems.",
                "Collaboration with the team to improve software architecture."
            ],
            "is_highlighted": True,
            "order": 1
        },
        {
            "title_it": "Cameriere",
            "title_en": "Waiter",
            "company": "Ristorante \"Al Gusto\"",
            "date_it": "Agosto 2023 - Maggio 2024",
            "date_en": "August 2023 - May 2024",
            "location": "Trento, TN",
            "tasks_it": [
                "Gestione dell'accoglienza e servizio clienti.",
                "Sviluppo di capacità di comunicazione, problem-solving e gestione ottimale dello stress e del tempo."
            ],
            "tasks_en": [
                "Welcoming guests and customer service management.",
                "Development of communication, problem-solving, and optimal stress and time management skills."
            ],
            "is_highlighted": False,
            "order": 2
        }
    ]

    education_data = [
        {
            "title_it": "Laurea Triennale in Informatica",
            "title_en": "Bachelor's Degree in Computer Science",
            "school": "Università di Trento",
            "date_it": "Settembre 2024 - Presente",
            "date_en": "September 2024 - Present",
            "location": "Trento, TN",
            "tasks_it": [
                "Acquisizione di solide basi matematiche e informatiche, con focus su algoritmi, strutture dati, programmazione e architetture di sistema.",
                "Sviluppo di un rigoroso approccio ingegneristico e scientifico per l'analisi di problemi complessi e la progettazione di soluzioni software.",
                "Studio approfondito di Ingegneria del Software, Sistemi Operativi, Reti, Basi di Dati e Logica Computazionale."
            ],
            "tasks_en": [
                "Acquisition of solid mathematical and computer science foundations, focusing on algorithms, data structures, programming, and system architectures.",
                "Development of a rigorous engineering and scientific approach to complex problem analysis and software solution design.",
                "In-depth study of Software Engineering, Operating Systems, Networks, Databases, and Computational Logic."
            ],
            "is_highlighted": True,
            "order": 1
        }
    ]

    skills_data = [
        {
            "title_it": "Programmazione", "title_en": "Programming",
            "icon_class": "fas fa-code",
            "skills_list_it": "Sviluppo di applicazioni, giochi e script con C++, C#, Rust, Python, Java, Javascript e Bash.",
            "skills_list_en": "Application, game, and scripts development using C++, C#, Rust, Python, Java, Javascript and Bash.",
            "order": 1
        },
        {
            "title_it": "Sviluppo Web", "title_en": "Web Development",
            "icon_class": "fas fa-laptop-code",
            "skills_list_it": "Creazione di SPA, MPA e API RESTful con FastAPI, Node.js e Express.",
            "skills_list_en": "Building SPAs, MPAs and RESTful APIs using FastAPI, Node.js and Express.",
            "order": 2
        },
        {
            "title_it": "Database", "title_en": "Databases",
            "icon_class": "fas fa-database",
            "skills_list_it": "Progettazione e modellazione di database SQL (MySQL e MariaDB) e NoSQL (MongoDB).",
            "skills_list_en": "Design and data modeling for SQL (MySQL e MariaDB) and NoSQL (MongoDB) databases.",
            "order": 3
        },
        {
            "title_it": "DevOps & Cloud", "title_en": "DevOps & Cloud",
            "icon_class": "fas fa-cloud",
            "skills_list_it": "Containerizzazione con Docker, Nginx e Linux.",
            "skills_list_en": "Containerization with Docker, Nginx and Linux.",
            "order": 4
        }
    ]

    interests_data = [
        {
            "title_it": "Corso coristico e strumentale", "title_en": "Choir and Instrumental Course",
            "organization": "I Minipolifonici",
            "date_it": "2013 - Presente", "date_en": "2013 - Present",
            "location": "Trento, TN",
            "description_it": "Studio strumentale e pratica orchestrale in ensemble di vario tipo e livello.",
            "description_en": "Instrumental study and orchestral practice in various ensembles.",
            "tasks_it": [
                "Membro del coro giovanile \"I Minipolifonici\", con esibizioni in Italia e all'estero.",
                "Partecipazione a eventi e concorsi prestigiosi, ottenendo riconoscimenti e premi.",
                "Sviluppo di capacità di lavoro di squadra, disciplina e interpretazione."
            ],
            "tasks_en": [
                "Member of the youth choir \"I Minipolifonici\", with performances in Italy and abroad.",
                "Participation in prestigious events and competitions, obtaining awards and recognition.",
                "Development of teamwork, discipline, and interpretation skills."
            ],
            "order": 1
        }
    ]

    languages_data = [
        {
            "title_it": "Italiano", "title_en": "Italian",
            "level_it": "Madrelingua", "level_en": "Native Speaker",
            "icon_class": "fas fa-language",
            "order": 1
        },
        {
            "title_it": "Inglese", "title_en": "English",
            "level_it": "Buona conoscenza (B2)", "level_en": "Fluent (B2)",
            "icon_class": "fas fa-globe-americas",
            "order": 2
        }
    ]

    print("🌱 Inizio il seeding del database...")

    for data in projects_data:
        if not db.query(Project).filter(Project.slug == data["slug"]).first():
            db.add(Project(**data))

    for data in experiences_data:
        if not db.query(Experience).filter(Experience.title_it == data["title_it"]).first():
            db.add(Experience(**data))

    for data in education_data:
        if not db.query(Education).filter(Education.title_it == data["title_it"]).first():
            db.add(Education(**data))

    for data in skills_data:
        if not db.query(SkillCategory).filter(SkillCategory.title_it == data["title_it"]).first():
            db.add(SkillCategory(**data))

    for data in interests_data:
        if not db.query(Interest).filter(Interest.title_it == data["title_it"]).first():
            db.add(Interest(**data))

    for data in languages_data:
        if not db.query(Language).filter(Language.title_it == data["title_it"]).first():
            db.add(Language(**data))

    db.commit()
    print("🎉 Modelli caricati nel DB!")

    db.close()

if __name__ == "__main__":
    seed_data()