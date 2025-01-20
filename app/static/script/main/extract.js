const filtros = document.querySelectorAll('.filtro-item');
            const transacoes = document.querySelectorAll('.transacao-item');

            filtros.forEach(filtro => {
                filtro.addEventListener('click', () => {
                    // Remove active class from all filters
                    filtros.forEach(f => f.classList.remove('active'));
                    // Add active class to clicked filter
                    filtro.classList.add('active');

                    const filtroTexto = filtro.textContent.toLowerCase();
                    
                    transacoes.forEach(transacao => {
                        if (filtroTexto === 'todos') {
                            transacao.style.display = 'grid';
                        } else if (filtroTexto === 'entradas') {
                            transacao.style.display = 
                                transacao.querySelector('.valor-entrada') ? 'grid' : 'none';
                        } else if (filtroTexto === 'saídas') {
                            transacao.style.display = 
                                transacao.querySelector('.valor-saida') ? 'grid' : 'none';
                        }
                    });
                });
            });