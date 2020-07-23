import React, { useState } from "react";
import {
    Button,
    Form,
    Alert,
} from "react-bootstrap";
import { Redirect } from "react-router-dom";


const CreateGamePage = () => {
    const [nickname, setNickname] = useState('');
    const [error, setError] = useState('');
    const [gameId, setGameId] = useState('');
    /*
        Submit nickname to createGame endpoint:
        Success: accept gameId, SPA redirect to game
        Error: too many games in progress, or something else went wrong
    */
    const createGame = (nickname) => {
        fetch(
            '/api/hb/create-game',
            {
                method: 'POST',
                body: JSON.stringify({nickname}),
                headers: {
                  'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
            }
        )
        .then(async response => {
            console.log({response});
            if (!response.ok) {
              setError(response.statusText);
              return response.statusText;
            } else {
                return await response.json();
            }
        })
        .then(json => {
            console.log({json});
            if (json.gameId) {
                setGameId(json.gameId);
            } else {
                setError('game id not found');
            }
        })
        .catch(e => setError(e));
    }
    return (
        <div>
            <h1>Create Game</h1>
            <Form onSubmit={() => createGame(nickname)}>
                <Form.Group controlId="formNickname">
                <Form.Label>Nickname</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="Enter nickname"
                    onChange={e => setNickname(e.target.value)}
                />
                <Form.Text className="text-muted">
                  Enter a nickname to create a new game.
                </Form.Text>
                </Form.Group>
                <Button variant="primary" onClick={() => createGame(nickname)}>
                    Create
                </Button>
                {error && <Alert type="error">Failed to create game: {error}</Alert>}
            </Form>
            {gameId !== '' && <Redirect to={`/hb/game/${gameId}`} />}
        </div>
    );
}

export default CreateGamePage;