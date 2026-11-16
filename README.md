# HCF — HandyCraftFlow

Личный кабинет селлера-производителя (самозанятый / ИП): учёт материалов, рецепты, производство, склад, экономика, акции МП.

## Архитектура

- **HCF Core** — учёт, экономика, интеграции с МП (WB, Ozon).
- **HCF Farm** — управление фермой 3D-принтеров.

## Стек

- Python 3.12, Django 6.x, DRF
- PostgreSQL 16, Redis, Celery
- React + TypeScript (в разработке)

## Локальный запуск

См. `docs/SETUP.md` (в разработке).

## Тесты

```bash
cd core && pytest apps/ -v          # Core: 166 passed
cd farm && pytest apps/printers/ -v # Farm: 32 passed