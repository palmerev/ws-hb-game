import "babel-polyfill";
import React, { useState } from "react";
import ReactDOM from "react-dom";
import {
    Button,
    Form,
    Alert,
} from "react-bootstrap";
import {
    BrowserRouter as Router,
    Route,
    Switch,
    NavLink,
    Redirect,
} from "react-router-dom";
import CreateGamePage from './components/CreateGamePage';

import './styles/index.scss';

const Nav = () => {
    return (
        <main>
          <nav>
            <ul>
              <li><NavLink to="/">Home</NavLink></li>
              <li><NavLink to="/create">Create</NavLink></li>
              <li><NavLink to="/join">Join</NavLink></li>
            </ul>
            </nav>
        </main>
    );
}

const HomePage = () => {
    return <div>
                <h1>Home</h1>
                <p>Example Form:</p>
                <Form>
                  <Form.Group controlId="formBasicEmail">
                    <Form.Label>Email address</Form.Label>
                    <Form.Control type="email" placeholder="Enter email" />
                    <Form.Text className="text-muted">
                      We'll never share your email with anyone else.
                    </Form.Text>
                  </Form.Group>
                  <Form.Group controlId="formBasicPassword">
                    <Form.Label>Username</Form.Label>
                    <Form.Control type="text" placeholder="Username" />
                  </Form.Group>
                  <Button variant="primary" type="submit">
                    Submit
                  </Button>
                </Form>
            </div>
}

const JoinPage = () => {
    return <div>
        <h1>Join Game</h1>
    </div>
}

const GamePage = (props) => {
    // const [players] = useState([]);
    console.log(props);
    const gameId = props.match.params.gameId;
    if (!gameId) {
        console.log('no gameId', gameId);
        return <p>What? No game id?</p>;
    }
    // fetch(
    //     url,
    //     {
    //         method: 'GET',
    //         headers: {
    //           'Accept': 'application/json',
    //           'Content-Type': 'application/json',
    //         },
    //         credentials: 'same-origin',
    //     }
    // )
    // .then(res => {
    //     // TODO: better error handling
    //     if (res.ok) {
    //         if (res.body.gameLocked) {
    //             throw new Error('Game locked!');
    //         }
    //     } else {
    //         throw res.statusText;
    //     }
    // });
    return (
        <div>
            <h1>Game Page for {gameId}! Woo!</h1>
        </div>
    )
}


class App extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            clientId: null,
            nickname: null,
            game: null,
        }
    }
    render() {
        return (
            <Router>
            <div className="container">
                <Nav />
                <Switch>
                    <Route path="/" exact component={HomePage} />
                    <Route path="/create" component={CreateGamePage} />
                    <Route path="/join" component={JoinPage} />
                    <Route path="/hb/game/:gameId" component={GamePage} />
                </Switch>
            </div>
            </Router>
        );
    }
}

const app = document.getElementById("app");

ReactDOM.render(<App />, app);
