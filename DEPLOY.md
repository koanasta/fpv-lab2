# Лабораторна робота №2 — розгортання середовища

## 1. Операційна система та версії ПЗ

| Компонент | Версія |
|---|---|
| ОС | Ubuntu 24.04.5 LTS (Noble), x86_64, у WSL 2 на Windows 11 |
| Ядро | 6.6.87.2-microsoft-standard-WSL2 |
| ROS 2 | Jazzy Jalisco (ros-jazzy-desktop 0.11.0) |
| Gazebo Sim | Harmonic 8.15.0 |
| ArduPilot | ArduPilot-4.6.0-beta1-8542-g14c871f273 (гілка master) |
| Python | 3.12.3 |
| Micro-XRCE-DDS-Gen | форк ArduPilot, гілка master |
| micro-ROS Agent | гілка jazzy |

### Чому Jazzy, а не Humble

У методичці наведено шлях `/opt/ros/humble`, але там же зазначено, що
«конкретні шляхи можуть відрізнятися залежно від способу встановлення».
ROS 2 Humble випускається лише для Ubuntu 22.04 (Jammy) і на Ubuntu 24.04
не встановлюється. Для Ubuntu 24.04 відповідним LTS-випуском є ROS 2 Jazzy,
який офіційно підтримується ArduPilot. Парна до Jazzy версія Gazebo —
Harmonic. Відповідно всюди замість `/opt/ros/humble/setup.bash`
використовується `/opt/ros/jazzy/setup.bash`.

## 2. Встановлення компонентів

### 2.1 ROS 2 Jazzy
```bash
sudo apt install ros-jazzy-desktop
```

### 2.2 Gazebo Harmonic
```bash
sudo apt install curl lsb-release gnupg wget
sudo curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
     -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
 | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
sudo apt update
sudo apt install gz-harmonic
sudo apt install ros-jazzy-ros-gz ros-jazzy-sdformat-urdf ros-jazzy-topic-tools
```

### 2.3 ArduPilot
```bash
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git ~/ardu_ws/src/ardupilot
cd ~/ardu_ws/src/ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

### 2.4 Генератор коду Micro-XRCE-DDS-Gen
Потрібен саме форк ArduPilot — версія від eProsima не підтримує ключ
`-default-container-prealloc-size`, який ArduPilot передає генератору,
і збірка падає з помилкою `Unknown argument`.

```bash
cd ~/ardu_ws
git clone --recurse-submodules https://github.com/ardupilot/Micro-XRCE-DDS-Gen.git
cd Micro-XRCE-DDS-Gen
git checkout master
./gradlew assemble
sudo ln -sf ~/ardu_ws/Micro-XRCE-DDS-Gen/scripts/microxrceddsgen /usr/local/bin/microxrceddsgen
```

### 2.5 Пакети інтеграції з Gazebo
Офіційний маніфест `ros2_gz.repos` розрахований на Humble, тому для Jazzy
складено власний файл `~/ardu_ws/ros2_gz.jazzy.repos`:

```yaml
repositories:
  ardupilot_gazebo:      { type: git, url: https://github.com/ArduPilot/ardupilot_gazebo.git, version: ros2 }
  ardupilot_gz:          { type: git, url: https://github.com/ArduPilot/ardupilot_gz.git,     version: main }
  ardupilot_sitl_models: { type: git, url: https://github.com/ArduPilot/SITL_Models.git,      version: main }
  micro_ros_agent:       { type: git, url: https://github.com/micro-ROS/micro-ROS-Agent.git,  version: jazzy }
```

```bash
cd ~/ardu_ws
vcs import --recursive --input ros2_gz.jazzy.repos src
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 2.6 Збірка робочого простору ArduPilot
```bash
cd ~/ardu_ws
source /opt/ros/jazzy/setup.bash
export GZ_VERSION=harmonic
colcon build --cmake-args -DBUILD_TESTING=ON
```

## 3. Робочий простір лабораторної роботи

```bash
mkdir -p ~/fpv_labs/src
cd ~/fpv_labs/src
ros2 pkg create fpv_lab2 \
    --build-type ament_python \
    --license Apache-2.0 \
    --dependencies rclpy std_srvs geometry_msgs nav_msgs ardupilot_msgs

cd ~/fpv_labs
source /opt/ros/jazzy/setup.bash
source ~/ardu_ws/install/setup.bash
colcon build --symlink-install --packages-select fpv_lab2
source ~/fpv_labs/install/setup.bash
ros2 pkg executables fpv_lab2
```

## 4. Скрипти швидкого запуску (Завдання 2)

Каталог `~/fpv_labs/scripts/`:

| Скрипт | Призначення |
|---|---|
| `setup_env.sh` | Спільне середовище: ROS 2, ardu_ws, fpv_labs, шляхи моделей і плагінів Gazebo. Підключається через `source`. |
| `start_sim.sh` | Запуск усього середовища однією командою: Gazebo (світ maze) + ArduPilot SITL + micro-ROS DDS-агент + RViz. Перед запуском сам викликає `stop_sim.sh`. |
| `stop_sim.sh` | Зупинка всіх процесів середовища та звільнення портів перед повторним запуском. |
| `run_flight_test.sh` | Завдання 3: запуск наданого прикладу (зліт, зависання, посадка). |
| `wait_ready.sh` | Очікує появи сервісів `/ap/v1` та успішного pre-arm. Викликається автоматично зі скриптів запуску польоту. |
| `run_goto_point.sh` | Завдання 4: політ до індивідуальної точки. Приймає `delta_x`, `delta_y` і необов'язковий `axis_direction`, веде журнал у `~/fpv_labs/logs/`. |

### Порядок запуску

Термінал 1:
```bash
~/fpv_labs/scripts/start_sim.sh
```

Термінал 2 — приклад викладача:
```bash
~/fpv_labs/scripts/run_flight_test.sh
```

Термінал 2 — власний алгоритм (замість 4.0 та 0.2 підставити свій варіант):
```bash
~/fpv_labs/scripts/run_goto_point.sh 4.0 0.2
```

Щоб виконати формулу Додатка 2 буквально (`x0 - Δx`), додається третій
аргумент — див. п. 6:
```bash
~/fpv_labs/scripts/run_goto_point.sh 4.0 0.2 -1
```

Зупинка:
```bash
~/fpv_labs/scripts/stop_sim.sh
```

## 5. Алгоритм польоту до заданої точки (Завдання 4)

Модуль `fpv_lab2/goto_point/` реалізовано як окремий пакет, який
**перевикористовує базові класи прикладу без змін**. Клас `GotoPointNode`
успадковано від `FlightTestNode`, вісім базових обробників станів узято
як є, замінено лише обробник стану `HOVERING` і додано два нові стани.

| Стан | Обробник | Дія |
|---|---|---|
| `WAITING_FOR_SYSTEM` … `TAKING_OFF` | базові, без змін | перевірка готовності, GUIDED, arm, зліт |
| `HOVERING` | `StabilizingHandler` | чекає фактичного досягнення висоти, потім стабілізація |
| `GOING_TO_TARGET` | `GoingToTargetHandler` | керування швидкістю з гальмуванням |
| `STOPPING` | `StoppingHandler` | гасить швидкість, друкує результат |
| `LANDING`, `WAITING_FOR_LANDING` | базові, без змін | посадка та завершення |

Нові стани оголошено в окремому `enum GotoState`; базовий `FlightState`
не змінювався. Обидва набори станів співіснують в одному словнику
обробників, оскільки словник Python допускає ключі різних типів.

### Закон керування

Поточне положення береться з теми `/odometry`. На кожному такті (5 Гц)
обчислюється вектор до цілі та відстань:

```
dx = x_target - x,  dy = y_target - y,  d = sqrt(dx^2 + dy^2)
```

Модуль швидкості пропорційний відстані з обмеженням зверху та знизу:

```
v = max(min_speed, max_speed * min(1, d / slowdown_radius))
vx = v * dx / d,   vy = v * dy / d
```

Команда публікується в тему `/ap/v1/cmd_vel` повідомленням
`geometry_msgs/TwistStamped` з `frame_id = "map"`. Для цього кадру
ArduPilot читає `twist.linear.x` як складову «на схід», а `twist.linear.y` —
«на північ», що збігається з осями `/odometry`.

Після досягнення цілі з похибкою, меншою за `tolerance`, публікується
нульова швидкість, програма чекає згасання залишкової швидкості, друкує
підсумок і перемикає апарат у режим LAND.

### Параметри вузла

| Параметр | За замовчуванням | Призначення |
|---|---|---|
| `delta_x`, `delta_y` | 0.0 | зміщення цілі за варіантом (Додаток 2) |
| `axis_direction` | 1.0 | напрямок осі зміщення (див. п. 6) |
| `takeoff_altitude` | 2.0 м | висота зльоту |
| `tolerance` | 0.25 м | допустима похибка досягнення цілі |
| `max_speed` | 1.5 м/с | максимальна горизонтальна швидкість |
| `min_speed` | 0.15 м/с | мінімальна швидкість підльоту |
| `slowdown_radius` | 2.5 м | радіус початку гальмування |
| `stabilize_duration` | 5.0 с | стабілізація після набору висоти |

### Результат виконання (варіант 8: Δx = 4,6; Δy = 1,4)

Команда запуску:

```bash
~/fpv_labs/scripts/run_goto_point.sh 4.6 1.4
```

Основні повідомлення програми:

```
Target offset applied: dx=+4.60 m, dy=+1.40 m (axis_direction=+1)
Start position:  x0=0.000 m, y0=0.000 m
Target position: x=4.600 m, y=1.400 m
Pre-arm check passed: Vehicle is Armable
GUIDED mode enabled
Motors armed
Requesting takeoff to 2.0 m
Take-off altitude reached: 1.83 m
Hover stabilised, starting flight to the target point
x=0.46 y=0.13 z=2.20 | distance 4.33 m | speed 1.50 m/s
x=1.77 y=0.53 z=2.20 | distance 2.96 m | speed 1.50 m/s
x=3.02 y=0.92 z=2.20 | distance 1.65 m | speed 0.99 m/s
x=3.87 y=1.17 z=2.19 | distance 0.77 m | speed 0.46 m/s
x=4.28 y=1.30 z=2.19 | distance 0.33 m | speed 0.20 m/s
Target reached, distance 0.233 m (tolerance 0.25 m)
----- RESULT -----
Start position:  x=0.000 y=0.000
Target position: x=4.600 y=1.400
Actual position: x=4.488 y=1.366 z=2.191
Position error:  e=0.117 m
------------------
Horizontal motion stopped, starting landing
LAND mode enabled
Landing completed
Final Gazebo altitude: 0.19 m
Flight test completed successfully
```

Зведення результатів:

| Показник | Значення |
|---|---|
| Початкове положення дрона | x₀ = 0,000 м; y₀ = 0,000 м |
| Задані координати цілі | x = 4,600 м; y = 1,400 м |
| Фактичні координати перед посадкою | x = 4,488 м; y = 1,366 м; z = 2,191 м |
| Похибка позиціонування | e = 0,117 м |
| Довжина маршруту | 4,81 м |
| Посадка | виконана автоматично, кінцева висота 0,19 м |

Похибка обчислена за формулою методички:

```
e = sqrt((4,488 - 4,600)^2 + (1,366 - 1,400)^2)
  = sqrt(0,012544 + 0,001156)
  = 0,117 м
```

Значення укладається в рекомендовані методичкою 0,2–0,3 м.

Перевірка прохідності маршруту для цього варіанта: найближча стіна
(`Wall_13`, x = 5, y від 2 до 7) віддалена від траєкторії на 0,72 м;
відстань цілі від старту 4,81 м, що відповідає твердженню Додатка 2
про мінімум 4 м.

## 6. Напрямок зміщення цілі — розбіжність із Додатком 2

Додаток 2 задає ціль як `x_target = x0 - Δx`, `y_target = y0 - Δy` і
водночас стверджує, що у світі `maze.sdf` прямі маршрути від старту до
заданих точок не перетинають стін.

Ці дві умови суперечать одна одній. Дрон стартує в точці (0, 0) кадру
`/odometry`, а стіна `Wall_9` світу `maze.sdf` проходить по `x = -1`
від `y = -1` до `y = 7`. Перевірка всіх 56 варіантів таблиці 2.3 дає:

| Напрямок | Варіантів перекрито стіною | Вільних |
|---|---|---|
| `x0 - Δx` (буквально за Додатком 2) | **56** | 0 |
| `x0 + Δx` | 0 | **56** |

У буквальному трактуванні маршрут упирається в стіну в усіх без винятку
варіантах (мінімальна відстань до стіни 0,00 м). Це підтверджено
експериментально: під час пробного польоту дрон дійшов до `x = -0,79`
і зіткнувся зі стіною, після чого ArduPilot видав
`Crash: Disarming: AngErr=37>30`.

У протилежному напрямку всі 56 маршрутів вільні із запасом понад 0,6 м,
що відповідає твердженню методички. Отже вісь, у якій Додаток 2 задає
зміщення, протилежна осі `x` теми `/odometry`.

Тому напрямок винесено в параметр `axis_direction`:

* `axis_direction = 1` (за замовчуванням) — ціль `x0 + Δx`, маршрут вільний;
* `axis_direction = -1` — буквально за формулою Додатка 2.

**Це питання варто узгодити з викладачем** — можливо, малася на увазі
інша система координат для `x0`, `y0`.

## 7. Проблеми, виявлені під час розгортання, та їх усунення

**Збірка падала на `ardupilot_sitl`** з помилкою
`Unknown argument -default-container-prealloc-size`. Причина:
`/usr/local/bin/microxrceddsgen` вказував на клон eProsima замість форку
ArduPilot. Виправлення: зібрано форк ArduPilot (`./gradlew assemble`),
симлінк перенаправлено на нього.

**`ros2 launch` аварійно завершувався** з `package 'topic_tools' not found`.
Пакет не входить у `ros-jazzy-desktop`. Виправлення:
`sudo apt install ros-jazzy-topic-tools`.

**`robot_state_publisher` падав, модель не зʼявлялася в Gazebo.** Файл
`iris_lidar.launch.py` замінює `model://` на `package://`, що не
резолвиться в Jazzy: libsdformat повідомляє
`Tried to use callback in sdf::findFile(), but the callback is empty`.
Виправлення: заміну закоментовано, до `SDF_PATH` додано каталог моделей
`ardupilot_gz_description`.

**Повторний запуск не працював:** `bind failed on port 5760 - Address
already in use`. Попередні процеси не встигали звільнити порти.
Виправлення: `stop_sim.sh` доопрацьовано — SIGTERM, потім SIGKILL, потім
очікування фактичного звільнення портів.

**`Vehicle is not armable` одразу після старту** — EKF ще не збігся на
розвʼязку GPS. Виправлення: `wait_ready.sh` чекає успішного pre-arm перед
запуском вузла.

**Дрон не злітав, хоча команда зльоту приймалася.** Вузол публікував
нульову швидкість у `/ap/v1/cmd_vel` під час зльоту, а команда швидкості
в режимі GUIDED перебиває виконання команди TAKEOFF. Виправлення: під час
зльоту команди швидкості не надсилаються взагалі.

**Pre-arm проходив у скрипті очікування, але падав у вузлі за дві секунди.**
Одразу після збіжності EKF автопілот «мерехтить» на межі: на один запит
відповідає `Vehicle is Armable`, а на наступний — `Vehicle is Not Armable`.
Скрипт `wait_ready.sh` бачив один позитивний відповідь і віддавав керування
вузлу, який одразу отримував негативну і зупинявся з помилкою. Виправлення
двостороннє: `wait_ready.sh` тепер вимагає **три позитивні відповіді
поспіль** (лічильник обнуляється при будь-якій негативній), а в модулі
`goto_point` базовий обробник pre-arm замінено на `RetryingPrearmCheckHandler`,
який повторює перевірку кожні 3 с протягом 180 с і зупиняється з помилкою
лише якщо апарат так і не став готовим.

**`Drone disarmed unexpectedly` одразу після arm.** Тема `/ap/v1/status`
оновлюється повільніше за цикл керування, тому перша ж перевірка бачила
застаріле `armed=False`. Виправлення: прапорець `seen_armed` — відсутність
arm вважається збоєм лише після того, як апарат був озброєний.

## 8. Особливості та обмеження

* Середовище працює у WSL 2. Графіка Gazebo та RViz виводиться через WSLg
  (`DISPLAY=:0`), окремий X-сервер не потрібен.
* Використано ROS 2 Jazzy та Gazebo Harmonic замість Humble — це вимога
  Ubuntu 24.04 (див. п. 1).
* Коефіцієнт реального часу симуляції становить 0,2–0,3, тобто симуляція
  йде приблизно втричі-вчетверо повільніше за реальний час. Повний цикл
  «зліт — політ до точки — посадка» займає 2–4 хвилини реального часу.
  Вузьке місце — сам сервер Gazebo: процес `gz sim -s` займає близько
  380 % CPU (майже 4 ядра з 12). Перемикання на 2D-лідар
  (`lidar_dim:=2`) та вимкнення RViz (`rviz:=false`) помітного приросту
  не дають — перевірено вимірюванням. Якщо знімки екрана не потрібні,
  можна запустити без графічного інтерфейсу Gazebo:

  ```bash
  ~/fpv_labs/scripts/start_sim.sh use_gz_sim_gui:=false
  ```

  Це вивільняє ще близько 1,4 ядра.
* Не слід запускати кілька польотів підряд без перезапуску симуляції:
  дрон стартує з точки попередньої посадки, а не з початку координат,
  і зміщення за варіантом відлічується вже від неї. Перед вимірювальним
  польотом середовище треба перезапустити, щоб старт був у точці (0, 0).
* Сервіс `/gui/screenshot` під WSLg повертає успіх, але файл не зберігає.
  Знімки екрана слід робити засобами Windows (`Win+Shift+S`) з вікна
  Gazebo.
* Перед кожним повторним запуском слід виконувати `stop_sim.sh`.
* У системі не має залишатися клон Micro-XRCE-DDS-Gen від eProsima: якщо
  `/usr/local/bin/microxrceddsgen` вказує на нього, збірка
  `ardupilot_sitl` падає на етапі генерації IDL.
