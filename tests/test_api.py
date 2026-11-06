import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as achados

ITEM = {"tipo": "perdido", "titulo": "Carteira preta", "categoria": "Documentos", "local": "Biblioteca", "descricao": "Com RG", "contato_email": "ana@unima.edu.br", "contato_telefone": "(82) 99999-8888"}


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        achados.app.config.update(DATABASE=self.tmp.name, TESTING=True)
        achados.init_db()
        self.c = achados.app.test_client()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def cadastrar(self, email="ana@unima.edu.br", client=None):
        return (client or self.c).post("/api/register", json={"nome": "Ana", "email": email, "senha": "123456"})

    def test_CT01_cadastro_e_login(self):
        self.assertEqual(self.cadastrar().status_code, 201)
        self.assertEqual(self.cadastrar().status_code, 409)  # e-mail duplicado
        self.c.post("/api/logout")
        self.assertEqual(self.c.post("/api/login", json={"email": "ana@unima.edu.br", "senha": "errada"}).status_code, 401)
        self.assertEqual(self.c.post("/api/login", json={"email": "ana@unima.edu.br", "senha": "123456"}).status_code, 200)

    def test_CT02_registrar_item_exige_login_e_aparece_na_lista(self):
        self.assertEqual(self.c.post("/api/itens", json=ITEM).status_code, 401)
        self.cadastrar()
        self.assertEqual(self.c.post("/api/itens", json=ITEM).status_code, 201)
        self.assertEqual(self.c.post("/api/itens", json={**ITEM, "titulo": ""}).status_code, 400)
        lista = self.c.get("/api/itens").get_json()
        self.assertEqual([i["titulo"] for i in lista], ["Carteira preta"])

    def test_CT03_busca_e_filtros(self):
        self.cadastrar()
        self.c.post("/api/itens", json=ITEM)
        self.c.post("/api/itens", json={**ITEM, "tipo": "achado", "titulo": "Chave do armário", "categoria": "Chaves", "local": "Cantina"})
        self.assertEqual(len(self.c.get("/api/itens?q=chave").get_json()), 1)
        self.assertEqual(len(self.c.get("/api/itens?tipo=achado").get_json()), 1)
        self.assertEqual(len(self.c.get("/api/itens?categoria=Documentos").get_json()), 1)
        self.assertEqual(len(self.c.get("/api/itens?q=inexistente").get_json()), 0)

    def test_CT04_marcar_devolvido_somente_pelo_dono(self):
        self.cadastrar()
        iid = self.c.post("/api/itens", json=ITEM).get_json()["id"]
        outro = achados.app.test_client()
        self.cadastrar("beto@unima.edu.br", outro)
        self.assertEqual(outro.post(f"/api/itens/{iid}/devolver").status_code, 403)
        self.assertEqual(self.c.post(f"/api/itens/{iid}/devolver").status_code, 200)
        self.assertEqual(self.c.get("/api/itens?status=devolvido").get_json()[0]["id"], iid)

    def test_CT05_editar_e_excluir(self):
        self.cadastrar()
        iid = self.c.post("/api/itens", json=ITEM).get_json()["id"]
        r = self.c.put(f"/api/itens/{iid}", json={**ITEM, "titulo": "Carteira marrom"})
        self.assertEqual(r.get_json()["titulo"], "Carteira marrom")
        self.assertEqual(self.c.delete(f"/api/itens/{iid}").status_code, 200)
        self.assertEqual(self.c.get("/api/itens").get_json(), [])

    def test_CT06_contato_oculto_para_visitante(self):
        self.cadastrar()
        self.c.post("/api/itens", json=ITEM)
        visitante = achados.app.test_client()
        self.assertIsNone(visitante.get("/api/itens").get_json()[0]["contato"])
        self.assertEqual(self.c.get("/api/itens").get_json()[0]["contato"],
                         {"email": "ana@unima.edu.br", "telefone": "82999998888"})

    def test_CT07_contato_email_telefone_ou_ambos(self):
        self.cadastrar()
        sem = {**ITEM, "contato_email": "", "contato_telefone": ""}
        self.assertEqual(self.c.post("/api/itens", json=sem).status_code, 400)
        so_tel = {**ITEM, "contato_email": ""}
        self.assertEqual(self.c.post("/api/itens", json=so_tel).status_code, 201)
        so_email = {**ITEM, "contato_telefone": ""}
        self.assertEqual(self.c.post("/api/itens", json=so_email).status_code, 201)
        self.assertEqual(self.c.post("/api/itens", json={**ITEM, "contato_telefone": "123"}).status_code, 400)
        self.assertEqual(self.c.post("/api/itens", json={**ITEM}).status_code, 201)  # ambos


if __name__ == "__main__":
    unittest.main(verbosity=2)
