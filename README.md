# Display Library Generator

Uma ferramenta visual e open-source desenvolvida em Python (Tkinter) para engenheiros e makers. Este software permite desenhar gráficos, ícones e sprites em uma interface gráfica amigável e exportá-los automaticamente como arquivos de cabeçalho (`.h`) prontos para serem incluídos em projetos de microcontroladores (STM32, ESP32, Arduino).

[![Download Executável](https://img.shields.io/badge/Download_EXE-Versão_1.0.0-blue?style=for-the-badge)](https://github.com/KevinRyanSF/DisplayLibraryGenerator/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python)](https://www.python.org/)

## Funcionalidades

* **Pintura Dinâmica:** Clique e arraste com o botão esquerdo para desenhar (simulando os pixels acesos do OLED) e botão direito para apagar.
* **Tamanhos Customizáveis:** Defina larguras e alturas independentes para cada sprite criado (ex: 8x8, 16x32, 128x64).
* **Engenharia Reversa (.h para UI):** Importe arquivos `.h` gerados anteriormente para continuar editando seus sprites visuais.
* **Múltiplos Gráficos:** Crie, nomeie e gerencie vários sprites na mesma sessão para exportá-los em uma única biblioteca unificada.
* **Código C Otimizado:** A exportação gera matrizes bidimensionais compactadas em arrays hexadecimais unidimensionais, economizando memória Flash do seu microcontrolador.

---

## Como Instalar e Executar

### Opção 1: Uso Rápido (Executável Windows)

Esta versão é portátil e não requer configuração de código.

1. Acesse a aba Releases e baixe o arquivo `Display_Library_Generator.exe`.
2. Execute o arquivo e comece a desenhar.

### Opção 2: Desenvolvedor (Executando pelo Código Fonte)

```bash
# 1. Clone o repositório
git clone https://github.com/SeuUsuario/DisplayLibraryGenerator.git
cd DisplayLibraryGenerator

# 2. Execute a aplicação (Utiliza apenas bibliotecas nativas do Python)
python main.py
```

### Opção 3: Gerando o seu próprio Executável (Build)

Para compilar o código fonte em um arquivo .exe stand-alone:

```bash
# Execute o script de automação na raiz do projeto
python build.py
```

O executável final será salvo na pasta `dist/`.

---

## Como utilizar a biblioteca gerada no seu Microcontrolador

Ao clicar em "Exportar .h" no programa, ele gerará um arquivo de cabeçalho (ex: `sprites.h`) contendo os metadados e os arrays constantes. Abaixo estão as orientações de como usar esse arquivo nos ecossistemas mais comuns.

---

### 1. Arduino & ESP32 / ESP8266

Nestas plataformas, a biblioteca mais comum é a Adafruit_SSD1306. Coloque o arquivo exportado (ex: `sprites.h`) na mesma pasta do seu sketch `.ino`.

```cpp
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// 1. Inclua o arquivo gerado pelo Display Library Generator
#include "sprites.h" 

#define OLED_RESET -1
Adafruit_SSD1306 display(DISPLAY_WIDTH, DISPLAY_HEIGHT, &Wire, OLED_RESET);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  
  // 2. Desenhe o sprite. 
  // O programa gera automaticamente os macros de LARGURA e ALTURA com o nome do seu sprite.
  // Exemplo desenhando o sprite chamado "nave_espacial" na posição X=10, Y=20:
  display.drawBitmap(10, 20, nave_espacial, NAVE_ESPACIAL_WIDTH, NAVE_ESPACIAL_HEIGHT, WHITE);
  
  display.display();
}

void loop() {
}
```

Nota para AVR (Arduino Uno/Nano): Como esses chips têm pouca RAM, adicione a palavra-chave `PROGMEM` logo após `const uint8_t` dentro do `.h` gerado se for usar sprites muito grandes.

---

### 2. Ecossistema STM32 (HAL)

No STM32, a exibição no OLED geralmente é feita utilizando bibliotecas de terceiros portadas para a HAL. Copie o arquivo gerado para a sua pasta `Core/Inc`.

```c
#include "main.h"
#include "ssd1306.h" // Sua biblioteca de driver I2C

// 1. Inclua o arquivo gerado pelo Display Library Generator
#include "sprites.h" 

int main(void) {
  HAL_Init();
  // ... Configurações geradas pelo STM32CubeMX ...
  
  ssd1306_Init();
  ssd1306_Fill(Black);
  
  // 2. Desenhe o sprite na tela.
  // Os parâmetros: X, Y, array do gráfico, largura, altura e cor (White)
  ssd1306_DrawBitmap(5, 5, icone_bateria, ICONE_BATERIA_WIDTH, ICONE_BATERIA_HEIGHT, White);
  
  ssd1306_UpdateScreen();
  
  while (1) {
    // Loop principal
  }
}
```