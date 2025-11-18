import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageContent.css';

interface MessageContentProps {
    content: string;
    role: 'user' | 'assistant';
}

export function MessageContent({ content, role }: MessageContentProps) {
    if (role === 'user') {
        // Mensagens do usuário não precisam de markdown
        return <div className="message-content">{content}</div>;
    }

    // Mensagens do assistente são renderizadas com markdown
    return (
        <div className="message-content message-content--assistant">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    p: ({ children }) => <p className="markdown-p">{children}</p>,
                    strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
                    em: ({ children }) => <em className="markdown-em">{children}</em>,
                    code: ({ className, children, ...props }) => {
                        const isInline = !className;
                        if (isInline) {
                            return <code className="markdown-code-inline" {...props}>{children}</code>;
                        }
                        return <code className="markdown-code-block" {...props}>{children}</code>;
                    },
                    pre: ({ children }) => <pre className="markdown-pre">{children}</pre>,
                    ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
                    ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
                    li: ({ children }) => <li className="markdown-li">{children}</li>,
                    blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
                    h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
                    h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
                    h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
                    a: ({ href, children }) => (
                        <a href={href} target="_blank" rel="noopener noreferrer" className="markdown-link">
                            {children}
                        </a>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}

