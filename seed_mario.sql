-- Script para inserir o personagem Mario com suas frases
-- Execute no Railway, aba Database do MySQL

USE railway;

-- Insere o personagem Mario
INSERT INTO characters (
    name,
    description,
    catchphrase,
    personality_traits,
    image_url,
    who_is_character,
    created_at,
    updated_at
) VALUES (
    'Mario Bros',
    'Herói do Reino dos Cogumelos, encanador carismático e corajoso.',
    'It''s-a me, Mario!',
    'corajoso,otimista,engraçado',
    'https://www.nintendo.com/eu/media/images/08_content_images/others_2/characterhubs/supermariohub/MarioHub_Overview_Mario_sideimg_mario.png',
    'o famoso encanador italiano do Reino dos Cogumelos',
    NOW(),
    NOW()
);

-- Pega o ID do Mario que acabamos de inserir
SET @mario_id = LAST_INSERT_ID();

-- Insere as frases do Mario
INSERT INTO phrases (character_id, phrase, purpose, created_at, updated_at) VALUES
(@mario_id, 'Mamma mia!', 'para surpresa', NOW(), NOW()),
(@mario_id, 'It''s-a me, Mario!', 'para se apresentar', NOW(), NOW()),
(@mario_id, 'Let''s-a go!', 'para animar', NOW(), NOW()),
(@mario_id, 'Wahoo!', 'para comemorações', NOW(), NOW()),
(@mario_id, 'Here we go!', 'para começar algo', NOW(), NOW());

-- Verifica os dados inseridos
SELECT * FROM characters WHERE name = 'Mario Bros';
SELECT * FROM phrases WHERE character_id = @mario_id;

