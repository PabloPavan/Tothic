import io
from contextlib import redirect_stdout
from main import execute

def compile_and_run(source_code: str) -> None:
    execute(source_code, True, True, False)

def simulate_vm_execution(source_code: str) -> str:
    f = io.StringIO()
    with redirect_stdout(f):
        compile_and_run(source_code)
    return f.getvalue().strip()

def run_tests():
    test_cases = [
        {
            "name": "Print literal diretamente",
            "code": """
                namespace main {
                    print("Hello World");
                    halt();
                }
            """,
            "expected_output": ">> Hello World"
        },
        {
            "name": "Literal atribuído antes do print",
            "code": """
                namespace main {
                    auto msg = "Texto fixo";
                    print(msg);
                    halt();
                }
            """,
            "expected_output": ">> Texto fixo"
        },
        {
            "name": "Literal usado duas vezes",
            "code": """
                namespace main {
                    string a;
                    a = "Repetido";
                    print(a);
                    print("Repetido");
                    halt();
                }
            """,
            "expected_output": ">> Repetido\n>> Repetido"
        },
        {
            "name": "Função com retorno inteiro",
            "code": """
                namespace main {
                    int soma(int a, int b) {
                        return a + b;
                    }
                    auto resultado = soma(5, 6);
                    print(resultado);
                    halt();
                }
            """,
            "expected_output": ">> 11"
        },
        {
            "name": "Função que imprime dentro dela",
            "code": """
                namespace main {
                    int mensagem() {
                        print("Olá de dentro da função");
                        return 0;
                    }

                    auto x = mensagem();
                    halt();
                }
            """,
            "expected_output": ">> Olá de dentro da função"
        },
        {
            "name": "Retorno de string por função",
            "code": """
                namespace main {
                    string saudacao() {
                        return "Oi";
                    }

                    auto msg = saudacao();
                    print(msg);
                    print("Tudo bem?");
                    halt();
                }
            """,
            "expected_output": ">> Oi\n>> Tudo bem?"
        }
    ]

    print("\n--- Resultados dos Testes de Literais ---\n")
    for i, case in enumerate(test_cases, 1):
        print(f"Teste {i}: {case['name']}")
        try:
            output = simulate_vm_execution(case["code"])
            success = output == case["expected_output"]
            print("✔️  Sucesso" if success else "❌  Falhou")
            print("Esperado:")
            print(case["expected_output"])
            print("Obtido:")
            print(output)
        except Exception as e:
            print("❌  Erro de execução:", e)
        print("-" * 40)

run_tests()