CREATE TABLE IF NOT EXISTS items (
  id serial PRIMARY KEY,
  name varchar(200) NOT NULL,
  description text
);

INSERT INTO items (name, description)
VALUES
  ('Exemple 1', 'Premier item inséré automatiquement'),
  ('Exemple 2', 'Deuxième item');
