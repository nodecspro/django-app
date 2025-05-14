<div id="readme-top"></div>

<!-- Language Switcher -->
<div align="center">
  <strong>Languages:</strong>
  <a href="#readme-russian">Русский</a> | 
  <a href="#readme-english">English</a>
</div>
<br>

---

<!-- English Version -->
<div id="readme-english">

<div align="right"><a href="#readme-top">Back to top ↑</a></div>

# Django Tree Menu Application

This is a Django application that implements a tree-like menu. The menu is rendered using a template tag, stored in a database, editable via the standard Django admin interface, and dynamically highlights the active item based on the current page URL.

## Features

*   **Template Tag Driven:** Menu rendering is handled by a custom `{% draw_menu 'menu_name' %}` template tag.
*   **Dynamic Expansion:**
    *   All parent items of the currently active menu item are expanded.
    *   The first level of child items under the active menu item is also expanded.
*   **Database Backed:** Menu items are stored in the database using a Django model.
*   **Admin Editable:** Menus can be created, updated, and deleted through the standard Django admin interface.
*   **URL-Based Active Item:** The active menu item is determined by matching its URL (either explicit or named) with the current page's URL.
*   **Multiple Menus:** Supports multiple distinct menus on a single page, identified by a unique menu name.
*   **Flexible URLs:** Menu items can link to explicit URLs or named URL patterns.
*   **Optimized Performance:** Each menu rendering requires exactly one database query.
*   **Dependencies:** Uses only Django and the Python standard library.

## Setup and Usage

### Prerequisites

*   Python (3.8+ recommended)
*   Django (4.x, 5.x recommended)

### Installation

1.  **Clone the repository or add the `treemenu` app to your Django project.**
    ```bash
    # If it's a standalone app you're adding to an existing project:
    # Place the 'treemenu' app directory into your project structure.
    ```

2.  **Add `treemenu` to `INSTALLED_APPS` in your project's `settings.py`:**
    ```python
    # myproject/settings.py
    INSTALLED_APPS = [
        # ... other apps
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'treemenu', # Add this line
    ]
    ```

3.  **Ensure `django.template.context_processors.request` is in your `TEMPLATES` setting:**
    This is required for the template tag to access the current request and determine the active URL.
    ```python
    # myproject/settings.py
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [], # Or your project-level template dirs
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request', # Ensure this is present
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    ```

4.  **Run migrations:**
    ```bash
    python manage.py makemigrations treemenu
    python manage.py migrate
    ```

5.  **Create a superuser (if you haven't already) to access the admin panel:**
    ```bash
    python manage.py createsuperuser
    ```

### Configuration

1.  **Access the Django Admin Panel:**
    Start your development server (`python manage.py runserver`) and navigate to `/admin/`.

2.  **Add Menu Items:**
    *   Go to the "Treemenu" section and click on "Menu items".
    *   Click "Add Menu item".
    *   Fill in the details:
        *   **Display Name:** The text shown for the menu item.
        *   **Menu Name:** A unique identifier for the menu this item belongs to (e.g., `main_menu`, `sidebar_menu`). This name will be used in the template tag.
        *   **Parent Item:** (Optional) Select a parent item to create a hierarchy.
        *   **Explicit URL:** A direct URL path (e.g., `/about/`).
        *   **Named URL:** The name of a URL pattern defined in your `urls.py` (e.g., `myapp:home_view`). Named URL takes precedence if both are provided and the named URL resolves successfully.
        *   **Order:** An integer to control the display order of items at the same level (lower numbers appear first).

### Usage in Templates

1.  **Load the template tag library** at the top of your template:
    ```html
    {% load menu_tags %}
    ```

2.  **Render the menu** using the `draw_menu` tag, passing the `menu_name` you defined in the admin:
    ```html
    <h2>Main Navigation</h2>
    {% draw_menu 'main_menu' %}

    <h2>Sidebar Links</h2>
    {% draw_menu 'sidebar_menu' %}
    ```

    The template tag will render the menu using `treemenu/templates/treemenu/menu_template.html` and `treemenu/templates/treemenu/menu_recursive_item.html`. You can customize these templates if needed.

### Example Structure

You can find example URL configurations and a sample page template (`page_example.html`) within the `treemenu` app for testing purposes. To use them:

1.  Include `treemenu.urls` in your project's `urls.py`:
    ```python
    # myproject/urls.py
    from django.urls import path, include
    from django.views.generic.base import RedirectView

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('menu-test/', include('treemenu.urls')), # Or any prefix you prefer
        # Optional: Redirect root to the menu test page
        path('', RedirectView.as_view(pattern_name='treemenu:home', permanent=False)),
    ]
    ```
    *Ensure `app_name = 'treemenu'` is set in `treemenu/urls.py` if using namespaced URLs like `treemenu:home`.*

2.  Navigate to `/menu-test/` (or the prefix you chose) in your browser.

## Customization

*   **Styling:** The generated HTML has classes like `active`, `expanded`, `collapsed`, and `menu-container menu-<menu_name_slugified>` that you can use for CSS styling.
*   **Templates:** You can override the default menu rendering templates (`menu_template.html`, `menu_recursive_item.html`) by creating files with the same names in your project's `templates/treemenu/` directory or within an app that appears before `treemenu` in `INSTALLED_APPS`.

<div align="right"><a href="#readme-top">Back to top ↑</a></div>
</div>

---
<br>

<!-- Russian Version -->
<div id="readme-russian">

<div align="right"><a href="#readme-top">К началу ↑</a></div>

# Django-приложение "Древовидное меню"

Это Django-приложение, реализующее древовидное меню. Меню отрисовывается с помощью шаблонного тега, хранится в базе данных, редактируется через стандартную админ-панель Django и динамически подсвечивает активный пункт на основе URL текущей страницы.

## Возможности

*   **Управление через шаблонный тег:** Отрисовка меню осуществляется с помощью пользовательского тега `{% draw_menu 'menu_name' %}`.
*   **Динамическое раскрытие:**
    *   Все родительские пункты текущего активного пункта меню раскрыты.
    *   Первый уровень дочерних пунктов под активным пунктом меню также раскрыт.
*   **Хранение в базе данных:** Пункты меню хранятся в базе данных с использованием Django-модели.
*   **Редактирование в админ-панели:** Меню можно создавать, обновлять и удалять через стандартный интерфейс администратора Django.
*   **Активный пункт на основе URL:** Активный пункт меню определяется путем сопоставления его URL (явного или именованного) с URL текущей страницы.
*   **Несколько меню:** Поддержка нескольких различных меню на одной странице, идентифицируемых по уникальному имени меню.
*   **Гибкие URL-адреса:** Пункты меню могут ссылаться на явные URL-адреса или на именованные URL-паттерны.
*   **Оптимизированная производительность:** Каждая отрисовка меню требует ровно одного запроса к базе данных.
*   **Зависимости:** Используются только Django и стандартная библиотека Python.

## Настройка и использование

### Требования

*   Python (рекомендуется 3.8+)
*   Django (рекомендуется 4.x, 5.x)

### Установка

1.  **Клонируйте репозиторий или добавьте приложение `treemenu` в ваш Django-проект.**
    ```bash
    # Если это отдельное приложение, которое вы добавляете в существующий проект:
    # Поместите директорию приложения 'treemenu' в структуру вашего проекта.
    ```

2.  **Добавьте `treemenu` в `INSTALLED_APPS` в файле `settings.py` вашего проекта:**
    ```python
    # myproject/settings.py
    INSTALLED_APPS = [
        # ... другие приложения
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'treemenu', # Добавьте эту строку
    ]
    ```

3.  **Убедитесь, что `django.template.context_processors.request` присутствует в настройках `TEMPLATES`:**
    Это необходимо, чтобы шаблонный тег мог получить доступ к текущему запросу и определить активный URL.
    ```python
    # myproject/settings.py
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [], # Или ваши директории шаблонов на уровне проекта
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request', # Убедитесь, что это присутствует
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    ```

4.  **Выполните миграции:**
    ```bash
    python manage.py makemigrations treemenu
    python manage.py migrate
    ```

5.  **Создайте суперпользователя (если еще не создан) для доступа к админ-панели:**
    ```bash
    python manage.py createsuperuser
    ```

### Конфигурация

1.  **Войдите в админ-панель Django:**
    Запустите сервер разработки (`python manage.py runserver`) и перейдите по адресу `/admin/`.

2.  **Добавьте пункты меню:**
    *   Перейдите в раздел "Treemenu" и выберите "Menu items".
    *   Нажмите "Add Menu item".
    *   Заполните поля:
        *   **Display Name:** Текст, отображаемый для пункта меню.
        *   **Menu Name:** Уникальный идентификатор меню, к которому принадлежит этот пункт (например, `main_menu`, `sidebar_menu`). Это имя будет использоваться в шаблонном теге.
        *   **Parent Item:** (Опционально) Выберите родительский пункт для создания иерархии.
        *   **Explicit URL:** Прямой URL-путь (например, `/about/`).
        *   **Named URL:** Имя URL-паттерна, определенного в вашем `urls.py` (например, `myapp:home_view`). Именованный URL имеет приоритет, если указаны оба и именованный URL разрешается успешно.
        *   **Order:** Целое число для управления порядком отображения пунктов на одном уровне (меньшие числа отображаются первыми).

### Использование в шаблонах

1.  **Загрузите библиотеку шаблонных тегов** в начале вашего шаблона:
    ```html
    {% load menu_tags %}
    ```

2.  **Отрисуйте меню** с помощью тега `draw_menu`, передав `menu_name`, который вы определили в админ-панели:
    ```html
    <h2>Главная навигация</h2>
    {% draw_menu 'main_menu' %}

    <h2>Боковые ссылки</h2>
    {% draw_menu 'sidebar_menu' %}
    ```

    Шаблонный тег отрисует меню, используя `treemenu/templates/treemenu/menu_template.html` и `treemenu/templates/treemenu/menu_recursive_item.html`. При необходимости вы можете кастомизировать эти шаблоны.

### Пример структуры

Вы можете найти примеры конфигурации URL и шаблон тестовой страницы (`page_example.html`) внутри приложения `treemenu`. Для их использования:

1.  Подключите `treemenu.urls` в файле `urls.py` вашего проекта:
    ```python
    # myproject/urls.py
    from django.urls import path, include
    from django.views.generic.base import RedirectView

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('menu-test/', include('treemenu.urls')), # Или любой другой префикс
        # Опционально: Перенаправление с корневого пути на тестовую страницу меню
        path('', RedirectView.as_view(pattern_name='treemenu:home', permanent=False)),
    ]
    ```
    *Убедитесь, что `app_name = 'treemenu'` установлено в `treemenu/urls.py`, если используете именованные URL с пространством имен, такие как `treemenu:home`.*

2.  Перейдите по адресу `/menu-test/` (или выбранному вами префиксу) в браузере.

## Кастомизация

*   **Стилизация:** Сгенерированный HTML содержит классы, такие как `active`, `expanded`, `collapsed`, и `menu-container menu-<menu_name_slugified>`, которые можно использовать для CSS-стилизации.
*   **Шаблоны:** Вы можете переопределить стандартные шаблоны отрисовки меню (`menu_template.html`, `menu_recursive_item.html`), создав файлы с такими же именами в директории `templates/treemenu/` вашего проекта или внутри приложения, которое указано раньше `treemenu` в `INSTALLED_APPS`.

<div align="right"><a href="#readme-top">К началу ↑</a></div>
</div>