import React from "react";
import ReactDOM from "react-dom";
import {
    Button,
    Form,
} from "react-bootstrap";

import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";

import './styles/index.scss';

const Nav = () => {
    return (
        <main>
          <nav>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/create">Create</Link></li>
              <li><Link to="/join">Join</Link></li>
            </ul>
            </nav>
        </main>
    );
}

const HomePage = () => {
    return <div className="container">
                <h1>Home</h1>
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

const CreatePage = () => {
    return <div>
        <h1>Create Game</h1>
    </div>
}

const JoinPage = () => {
    return <div>
        <h1>Join Game</h1>
    </div>
}


class App extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            clientId: null,
            username: null,
            game: null,
        }
    }
    render() {
        return (
            <Router>
            <div>
                <Nav />
                <Switch>
                    <Route path="/" exact component={HomePage} />
                    <Route path="/create" component={CreatePage} />
                    <Route path="/join" component={JoinPage} />
                </Switch>
            </div>
            </Router>
        );
    }
}

const app = document.getElementById("app");

ReactDOM.render(<App />, app);