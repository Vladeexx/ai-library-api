async def test_create_book(client):
    response = await client.post("/api/v1/books/", json={
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "published_year": 2008,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert C. Martin"
    assert "id" in data


async def test_get_book(client):
    created = await client.post("/api/v1/books/", json={
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
    })
    book_id = created.json()["id"]

    response = await client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


async def test_get_book_not_found(client):
    response = await client.get("/api/v1/books/9999")
    assert response.status_code == 404


async def test_list_books(client):
    for i in range(3):
        await client.post("/api/v1/books/", json={"title": f"Book {i}", "author": "Author"})

    response = await client.get("/api/v1/books/")
    assert response.status_code == 200
    assert len(response.json()) == 3
