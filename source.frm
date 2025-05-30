Form apresentacao {
    Field nome String {
        required
        placeholder = "Digite seu nome"
        title = "Nome"
        description = "Digite seu nome completo"
    }
    Field idade Number {
        required
        placeholder = "Digite sua idade"
        title = "Idade"
        description = "Digite sua idade em anos"
    }
    Field genero Select {
        required
        placeholder = "Selecione seu gênero"
        title = "Gênero"
        description = "Selecione seu gênero"
        options = [
            "Masculino", 
            "Feminino", 
            "Outro"
        ]
    }
    Field data_nascimento Date {
        required
        placeholder = "Digite sua data de nascimento"
        title = "Data de Nascimento"
        description = "Qual é sua data de nascimento? Responda no formato YYYY-MM-DD"
    }
    Field hora_almoco Time {
        required
        placeholder = "Digite a sua hora de almoço"
        title = "Hora do almoço"
        description = "A que horas você costuma almoçar? Responda no formato: HH:MM"
    }
    Field curiosidade String {
        placeholder = "Digite uma curiosidade sobre você"
        title = "Curiosidade"
        description = "Fale uma coisa interessante sobre você, algo que ninguém sabe!"
    }
    validator {
        if (idade < 0) then {
            on[PAGE]display("idade inválida")
            cancel
        } else if (hora_almoco < "07:00" or hora_almoco > "18:00") then {
            on[PAGE]display("hora de almoço inválida")
            cancel
        } else if (data_nascimento < "1900-01-01") then {
            on[PAGE]display("data de nascimento inválida")
            cancel
        } else {
            on[PAGE]display("prazer em conhece-lo(a) " + nome)
            submit
        }
    }
}