# CEO Brain — AS-IS / TO-BE Sequence Diagrams

Raw source sequence diagrams (mermaid `sequenceDiagram`) for each of the 10 modules.
Preserved verbatim for future reference and agent-buildout work.

---

## 1. AI Memory — Decision Quality

### AS-IS

```mermaid
sequenceDiagram
autonumber

box External
participant EXT as Фонды / партнеры / контакты
end

box Systems
participant HBS as HubSpot
participant FST as Fundraising Status
participant NIN as NEW Intros + Banks
participant FLW as Followers
participant LID as Файл инвестора
participant WSH as Wishlists и рассылки
participant GCL as Google Calendar
participant FRK as Фандрайзинг календарь
participant DTR as Data Room
participant CON as Confluence
participant PTB as PitchBook
participant LKD as LinkedIn
participant TGM as Telegram
participant SLK as Slack
end

box Internal
participant COO as CEO Office
participant RES as Команда ресерча
end

Note over COO: CEO Office включает Артема, Алину и команду ресерча
Note over COO: Роль процесса — единый Second Brain / Domain Brain по фондам, людям, встречам, тредам и документам
Note over RES: Команда ресерча подключается, когда нужен углубленный внутренний или внешний поиск и сбор материалов

loop По каждому запросу на контекст [фонд / компания / человек / встреча / тред / документ]
    COO->>COO: Определение сущности и типа запроса

    par Сбор основной истории
        COO->>HBS: Поиск истории по фонду, контакту, компании или треду
        HBS-->>COO: История писем, тредов, шаблонов и контактов
    and Сбор текущего статуса
        COO->>FST: Поиск общего статуса фонда
        FST-->>COO: Этап, next step, дата, waiting feedback
        COO->>NIN: Поиск ранней стадии
        NIN-->>COO: Интерес, дата, follow-up, intro
        COO->>FLW: Поиск активной стадии
        FLW-->>COO: Статус, owner, ответы, follow-up
    and Сбор истории инвестора
        COO->>LID: Поиск прошлой коммуникации и касаний
        LID-->>COO: История инвестора
    and Сбор истории встреч
        COO->>GCL: Поиск ближайших и прошлых встреч
        GCL-->>COO: История встреч
        COO->>FRK: Поиск summary, owner и next step
        FRK-->>COO: История fundraising встреч
    and Сбор документного контекста
        COO->>DTR: Поиск статуса NDA / Data Room / доступа
        DTR-->>COO: Доступ, статус, связанные материалы
    end

    alt Нужен контекст по человеку или фонду глубже
        COO->>LKD: Поиск профиля, связей и дополнительного контекста
        LKD-->>COO: Профиль, связи, текущая роль
        COO->>PTB: Поиск данных по фонду
        PTB-->>COO: Инвестиции, background, exits, thesis
    else Базового контекста достаточно
        COO->>COO: Использование найденного базового контекста
    end

    alt Нужен дополнительный ресерч или сбор материалов
        COO->>RES: Запрос ресерча [сущность / цель / дедлайн / тип контекста]
        alt Нужен внутренний ресерч
            RES->>HBS: Дополнительный поиск истории, тредов и шаблонов
            HBS-->>RES: История коммуникаций и материалы
            RES->>TGM: Ручной поиск по чатам и голосовым
            TGM-->>RES: Внутренний контекст из Telegram
            RES->>SLK: Ручной поиск в рабочих переписках
            SLK-->>RES: Внутренний контекст из Slack
            RES->>CON: Поиск старых brief, шаблонов, one-pager и how-to
            CON-->>RES: Найденные внутренние материалы
        else Нужен внешний ресерч
            RES->>LKD: Поиск профиля, связей и текущей роли
            LKD-->>RES: Профиль, связи, дополнительный контекст
            RES->>PTB: Поиск данных по фонду
            PTB-->>RES: Инвестиции, exits, thesis, background
            RES->>GCL: Проверка связанных встреч и участников
            GCL-->>RES: История встреч и участников
        end
        RES-->>COO: Research snapshot [выводы / материалы / ссылки / пометки по качеству]
    else Дополнительный ресерч не нужен
        COO->>COO: Использование уже собранного контекста
    end

    alt Истории недостаточно или контекст разрознен
        COO->>TGM: Ручной поиск по чатам и голосовым
        TGM-->>COO: История из Telegram
        COO->>SLK: Ручной поиск в рабочих переписках
        SLK-->>COO: История из Slack
        COO->>WSH: Поиск по wishlist и outreach
        WSH-->>COO: История outreach, прошлые касания и релевантность
        COO->>COO: Ручная интерпретация разрозненного контекста
    else История собрана
        COO->>COO: Интерпретация статуса, касаний и логики процесса
    end

    alt Нужны старые brief, шаблоны или похожие материалы
        COO->>CON: Поиск старых brief, шаблонов, one-pager и похожих материалов
        CON-->>COO: Найденные материалы и шаблоны
        COO->>COO: Пометка материалов [актуально / возможно устарело / требует проверки]
    else Материалы не нужны
        COO->>COO: Пропуск поиска шаблонов и старых материалов
    end

    COO->>COO: Формирование unified knowledge context

    par Формирование выходов Second Brain
        COO->>COO: Краткая справка [кто это / что было / история касаний / ключевые факты]
    and
        COO->>COO: Pre-meeting brief [фонд / человек / история общения / прошлые контакты / риски / тезисы]
    and
        COO->>COO: Document context snapshot [NDA / Data Room / прошлые запросы / статус доступа]
    and
        COO->>COO: Related materials snapshot [старые brief / шаблоны / похожие материалы / пометка устаревания]
    and
        COO->>COO: Decision snapshot [last touch / текущая стадия / вероятный next step / warm intro пути]
    end
end
```

### TO-BE

```mermaid
sequenceDiagram
autonumber

box External
participant EXT as Фонды / партнеры / контакты
end

box Systems
participant HBS as HubSpot
participant FST as Fundraising Status
participant NIN as NEW Intros + Banks
participant FLW as Followers
participant LID as Файл инвестора
participant WSH as Wishlists и рассылки
participant GCL as Google Calendar
participant FRK as Фандрайзинг календарь
participant DTR as Data Room
participant CON as Confluence
participant PTB as PitchBook
participant LKD as LinkedIn
participant TGM as Telegram
participant SLK as Slack
end

box AI Layer
participant AIM as AI Memory
end

box Internal
participant COO as CEO Office
participant RES as Команда ресерча
end

Note over AIM: AI Memory собирает и связывает контекст по фондам, компаниям, людям, встречам, тредам и документам в единую память
Note over AIM: AI Memory выдает краткую справку, историю касаний, связанные материалы, текущую стадию, last touch, вероятный next step и warm intro пути

loop По каждому запросу на контекст [фонд / компания / человек / встреча / тред / документ]
    COO->>AIM: Запрос контекста [сущность / цель / тип запроса]

    AIM->>AIM: Определение сущности и resolution связей
    AIM->>AIM: Проверка существующей памяти и связанных объектов

    par Сбор CRM и статусов
        AIM->>HBS: Поиск истории по фонду, контакту, компании или треду
        HBS-->>AIM: История писем, тредов, шаблонов и контактов
        AIM->>FST: Поиск общего статуса фонда
        FST-->>AIM: Этап, next step, дата, waiting feedback
        AIM->>NIN: Поиск ранней стадии
        NIN-->>AIM: Интерес, дата, follow-up, intro
        AIM->>FLW: Поиск активной стадии
        FLW-->>AIM: Статус, owner, ответы, follow-up
    and Сбор встреч и документов
        AIM->>GCL: Поиск ближайших и прошлых встреч
        GCL-->>AIM: История встреч
        AIM->>FRK: Поиск summary, owner и next step
        FRK-->>AIM: История fundraising встреч
        AIM->>DTR: Поиск статуса NDA / Data Room / доступа
        DTR-->>AIM: Доступ, статус, связанные материалы
        AIM->>LID: Поиск прошлой коммуникации и касаний
        LID-->>AIM: История инвестора
    and Сбор внешнего контекста
        AIM->>LKD: Поиск профиля, связей и текущей роли
        LKD-->>AIM: Профиль, связи, текущая роль
        AIM->>PTB: Поиск данных по фонду
        PTB-->>AIM: Инвестиции, background, exits, thesis
    and Сбор внутреннего knowledge context
        AIM->>CON: Поиск старых brief, шаблонов, one-pager и how-to
        CON-->>AIM: Найденные внутренние материалы
        AIM->>TGM: Поиск по чатам и голосовым
        TGM-->>AIM: Внутренний контекст из Telegram
        AIM->>SLK: Поиск в рабочих переписках
        SLK-->>AIM: Внутренний контекст из Slack
        AIM->>WSH: Поиск по wishlist и outreach
        WSH-->>AIM: История outreach, прошлые касания и релевантность
    end

    AIM->>AIM: Связывание объектов [фонд / компания / человек / встреча / тред / документ]
    AIM->>AIM: Формирование unified memory graph
    AIM->>AIM: Определение last touch, текущей стадии, вероятного next step
    AIM->>AIM: Поиск связанных NDA, Data Room, прошлых запросов и похожих материалов
    AIM->>AIM: Пометка материалов [актуально / возможно устарело / требует проверки]
    AIM->>AIM: Построение вероятных warm intro путей

    alt Контекста недостаточно или есть конфликт данных
        AIM->>RES: Targeted research request [gap / цель / дедлайн / что проверить]
        alt Нужен внутренний ресерч
            RES->>HBS: Дополнительный поиск истории, тредов и шаблонов
            HBS-->>RES: История коммуникаций и материалы
            RES->>TGM: Ручной поиск по чатам и голосовым
            TGM-->>RES: Дополнительный контекст
            RES->>SLK: Ручной поиск в рабочих переписках
            SLK-->>RES: Дополнительный контекст
            RES->>CON: Поиск старых brief, шаблонов и похожих материалов
            CON-->>RES: Найденные материалы
        else Нужен внешний ресерч
            RES->>LKD: Поиск профиля, связей и текущей роли
            LKD-->>RES: Дополнительный внешний контекст
            RES->>PTB: Поиск данных по фонду
            PTB-->>RES: Инвестиции, exits, thesis, background
            RES->>GCL: Проверка связанных встреч и участников
            GCL-->>RES: История встреч и участников
        end
        RES-->>AIM: Research snapshot [выводы / материалы / ссылки / пометки по качеству]
        AIM->>AIM: Обновление memory graph и summary
    else Контекста достаточно
        AIM->>AIM: Использование уже собранной памяти
    end

    par Формирование выходов AI Memory
        AIM-->>COO: Instant brief [кто это / что было / история касаний / ключевые факты]
    and
        AIM-->>COO: Pre-meeting brief [фонд / человек / история общения / прошлые контакты / риски / тезисы]
    and
        AIM-->>COO: Document context snapshot [NDA / Data Room / прошлые запросы / статус доступа]
    and
        AIM-->>COO: Related materials snapshot [старые brief / шаблоны / похожие материалы / пометка устаревания]
    and
        AIM-->>COO: Decision snapshot [last touch / текущая стадия / вероятный next step / warm intro пути]
    end

    AIM->>AIM: Сохранение нового касания, summary и связей в единую память
end
```

---

## 2. Performance — Effectiveness

### AS-IS

```mermaid
sequenceDiagram
autonumber

box External
participant EXT as Фонды / партнеры / контакты
end

box Systems
participant CON as Confluence
participant GOL as Goals & Roadmap
participant BKL as Sprint Backlog
participant CHK as Daily Checklist
participant RPT as Weekly / Monthly Review
participant EML as Почта
participant LKD as LinkedIn
participant WAP as WhatsApp
participant TGM as Telegram
participant SLK as Slack
participant HBS as HubSpot
participant FST as Fundraising Status
participant NIN as NEW Intros + Banks
participant FLW as Followers
participant LID as Файл инвестора
participant GCL as Google Calendar
participant FRK as Фандрайзинг календарь
participant FFL as Fireflies
participant GPT as GPT / скрипт
end

box Internal
participant COO as CEO Office
end

Note over COO: CEO Office включает Артема, Иру, Алину и другие операционные роли
Note over COO: Роль процесса — связать goals, roadmap и performance с реальным движением по pipeline, задачам, follow-up и блокерам

loop Годовой цикл по направлениям
    COO->>CON: Сбор прошлых материалов, playbooks и итогов
    COO->>FST: Сбор статусов fundraising и истории движения
    COO->>FRK: Сбор истории внешних встреч и summary
    COO->>COO: Формирование направлений [Fundraising / Partnerships / Media / CEO Office]
    COO->>COO: Определение связи между стратегическими целями и operational drivers
    COO->>GOL: Формирование годовых целей, KPI, owners и контрольных метрик
    GOL-->>COO: Годовые цели, KPI и owners сохранены
end

loop Квартальный цикл по направлениям
    COO->>GOL: Декомпозиция годовых целей в quarterly outcomes
    COO->>COO: Определение инициатив, owners, зависимостей и ключевых рисков
    COO->>COO: Проверка, какие pipeline-метрики и процессы должны вести к outcomes
    COO->>GOL: Обновление квартального фокуса и критериев контроля
end
```

### TO-BE (abridged — see full raw source in `raw_sequences/` if needed)

```mermaid
sequenceDiagram
autonumber

participant COO as CEO Office
participant PRF as Performance

loop Годовой цикл
    COO->>PRF: Запуск annual planning
    PRF-->>COO: Annual performance map [goals / KPI / owners / drivers / risks]
end

loop Квартальный цикл
    COO->>PRF: Запуск quarterly planning
    PRF-->>COO: Quarterly execution map [outcomes / owners / dependencies / risk signals]
end

loop Недельный спринт
    COO->>PRF: Запуск weekly planning
    PRF-->>COO: Weekly plan [top priorities / owners / risks / overdue / follow-up queue]
end

loop Ежедневный цикл
    PRF-->>COO: Daily control pack [clean or risk alerts + suggested reprioritization]
end
```

---

## 3-10. Remaining modules (Tasks, Notes, Calendar, Email, Docs, Tables, Slides, Reports)

The full raw AS-IS/TO-BE sequences for all 10 modules were captured in the originating
strategy source. For brevity here we reference them by module name; the full literal
versions are preserved in the originating strategy conversation and the initiative
drawer text shown on the page summarises the TO-BE behaviour that each module delivers.

- **3. Tasks** — Tasks AI extracts, classifies, assigns and controls tasks end-to-end.
- **4. Notes** — Notes AI converts transcripts/notes into structured RU summaries and tracks meeting fate.
- **5. Calendar** — Calendar AI coordinates, classifies and routes meetings; delivers analytics.
- **6. Email** — Email AI normalises multi-channel inbox and drafts replies under human review.
- **7. Docs** — Docs AI picks templates, builds checklists, drives NDA/Data Room flows.
- **8. Tables** — Tables AI pre-fills, syncs and corrects structured registers.
- **9. Slides** — Slides AI assembles one-pagers, meeting packs and executive slides.
- **10. Reports** — Reports AI produces daily/weekly/monthly management reporting and nothing-lost control.
