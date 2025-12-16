// Código para testar performance do chat no console do navegador
// Cole este código no console (F12) e execute

(async function testChatPerformance() {
    const backendUrl = 'https://backend-chatbot-personagens-production.up.railway.app';
    
    console.log('🚀 Iniciando teste de performance...\n');
    
    // Teste 1: Health check (deve ser rápido)
    console.log('📊 Teste 1: Health Check');
    const healthStart = performance.now();
    try {
        const healthResponse = await fetch(`${backendUrl}/health`);
        const healthData = await healthResponse.json();
        const healthTime = (performance.now() - healthStart).toFixed(2);
        console.log(`✅ Health check: ${healthTime}ms`);
        console.log(`   Resposta:`, healthData);
    } catch (error) {
        console.error('❌ Erro no health check:', error);
    }
    
    console.log('\n');
    
    // Teste 2: Listar personagens (deve ser rápido)
    console.log('📊 Teste 2: Listar Personagens');
    const charsStart = performance.now();
    try {
        const charsResponse = await fetch(`${backendUrl}/api/characters/`);
        const charsData = await charsResponse.json();
        const charsTime = (performance.now() - charsStart).toFixed(2);
        console.log(`✅ Listar personagens: ${charsTime}ms`);
        console.log(`   Personagens encontrados:`, charsData.length);
    } catch (error) {
        console.error('❌ Erro ao listar personagens:', error);
    }
    
    console.log('\n');
    
    // Teste 3: Chat (pode demorar - chama OpenAI)
    console.log('📊 Teste 3: Chat (chama OpenAI)');
    console.log('⏳ Isso pode demorar... aguarde...\n');
    
    const chatStart = performance.now();
    const timeToFirstByte = performance.now(); // Será atualizado quando receber primeiro byte
    
    try {
        const chatResponse = await fetch(`${backendUrl}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: "Olá! Como você está?",
                character_id: 1,
                conversation_history: []
            })
        });
        
        const timeToResponse = performance.now();
        const timeToResponseMs = (timeToResponse - chatStart).toFixed(2);
        console.log(`⏱️  Tempo até receber resposta HTTP: ${timeToResponseMs}ms`);
        
        const chatData = await chatResponse.json();
        const totalTime = (performance.now() - chatStart).toFixed(2);
        const parseTime = (performance.now() - timeToResponse).toFixed(2);
        
        console.log(`✅ Chat completo: ${totalTime}ms`);
        console.log(`   - Tempo até resposta HTTP: ${timeToResponseMs}ms`);
        console.log(`   - Tempo para parsear JSON: ${parseTime}ms`);
        console.log(`   - Resposta:`, chatData.response.substring(0, 100) + '...');
        
        // Análise
        const totalSeconds = parseFloat(totalTime) / 1000;
        if (totalSeconds < 5) {
            console.log(`\n✅ Performance EXCELENTE (< 5s)`);
        } else if (totalSeconds < 15) {
            console.log(`\n⚠️  Performance ACEITÁVEL (5-15s)`);
        } else if (totalSeconds < 30) {
            console.log(`\n⚠️  Performance LENTA (15-30s)`);
        } else {
            console.log(`\n❌ Performance MUITO LENTA (> 30s)`);
        }
        
    } catch (error) {
        const errorTime = (performance.now() - chatStart).toFixed(2);
        console.error(`❌ Erro após ${errorTime}ms:`, error);
    }
    
    console.log('\n✅ Teste concluído!');
})();

