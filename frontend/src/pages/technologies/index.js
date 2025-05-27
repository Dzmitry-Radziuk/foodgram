import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
    <h1 className={styles.title}>Технологический стек</h1>
    <div className={styles.content}>
      <div>
        <h2 className={styles.subtitle}>Что стоит за FoodGram:</h2>
        <div className={styles.text}>
          <ul className={styles.list}>
            <li className={styles.textItem}>
              <strong>Python</strong> — основной язык для серверной логики и бизнес-правил.
            </li>
            <li className={styles.textItem}>
              <strong>Django</strong> — фреймворк, на котором построена архитектура веб-приложения.
            </li>
            <li className={styles.textItem}>
              <strong>Django REST Framework</strong> — библиотека для организации REST API.
            </li>
            <li className={styles.textItem}>
              <strong>Djoser</strong> — готовые эндпоинты для регистрации, аутентификации и управления пользователями.
            </li>
            <li className={styles.textItem}>
              <strong>PostgreSQL</strong> — реляционная СУБД для надёжного хранения данных.
            </li>
            <li className={styles.textItem}>
              <strong>Docker &amp; Docker Compose</strong> — контейнеризация сервисов и единый конфигурационный файл для быстрого деплоя.
            </li>
            <li className={styles.textItem}>
              <strong>Nginx</strong> — обратный прокси и веб-сервер для отдачи статики и балансировки запросов.
            </li>
            <li className={styles.textItem}>
              <strong>React</strong> — библиотека для создания интерактивного клиентского интерфейса.
            </li>
          </ul>
        </div>
      </div>
    </div>
  </Container>
  </Main>
}

export default Technologies

