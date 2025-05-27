import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Добро пожаловать на FoodGram!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что такое FoodGram?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              FoodGram — это ваш личный кулинарный дневник на просторах интернета<br/>
              Этот проект родился в процессе обучения в Яндекс Практикуме<br/>
              и спроектирован мной с нуля.
            </p>
            <p className={styles.textItem}>
              Делитесь авторскими рецептами, сохраняйте любимые блюда и всегда держите под рукой список ингредиентов для вашего следующего кулинарного шедевра. Подключайтесь к сообществу, чтобы смотреть рецепты друзей и открывать для себя новые вкусы.
            </p>
            <p className={styles.textItem}>
              Для полного доступа к функционалу необходимо зарегистрироваться.<br /> 
              Не переживайте об email-верификации — введите любой электронный адрес<br />
              и погружайтесь в мир кулинарии!
            </p>
            <p className={styles.textItem}>
              Присоединяйтесь к FoodGram и вдохновляйтесь новыми идеями каждый день!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>Полезные ссылки</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Исходный код: <a href="https://github.com/Dzmitry-Radziuk/foodgram/" className={styles.textLink}>GitHub</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="https://github.com/Dzmitry-Radziuk/" className={styles.textLink}>Дмитрий Радюк</a>
            </p>
          </div>
        </aside>
      </div>
    </Container>
  </Main>
}

export default About

