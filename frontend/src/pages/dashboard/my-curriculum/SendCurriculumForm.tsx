import React, { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import axios from 'axios';
import { 
  Upload, 
  Link as LinkIcon, 
  Code2, 
  FileText, 
  Plus, 
  Trash2, 
  Send, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';

export interface Skill {
  name: string;
  years: number;
}

interface StatusMessage {
  type: 'success' | 'error';
  text: string;
}

export default function SendCurriculumForm() {
  const [resumePdf, setResumePdf] = useState<File | null>(null);
  const [linkedinPdf, setLinkedinPdf] = useState<File | null>(null);
  const [githubUrl, setGithubUrl] = useState<string>('');
  const [portfolioUrl, setPortfolioUrl] = useState<string>('');
  
  const [skills, setSkills] = useState<Skill[]>([]);
  const [currentSkill, setCurrentSkill] = useState<string>('');
  const [currentYears, setCurrentYears] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<StatusMessage | null>(null);

  const handleResumeChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResumePdf(e.target.files[0]);
    }
  };

  const handleLinkedinChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setLinkedinPdf(e.target.files[0]);
    }
  };

  const handleAddSkill = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!currentSkill.trim()) return;

    const newSkill: Skill = {
      name: currentSkill.trim(),
      years: currentYears ? Number(currentYears) : 0,
    };

    setSkills((prev) => [...prev, newSkill]);
    setCurrentSkill('');
    setCurrentYears('');
  };

  const handleRemoveSkill = (index: number) => {
    setSkills((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!resumePdf) {
      setStatusMessage({ 
        type: 'error', 
        text: 'Por favor, anexe o PDF do seu currículo atual (obrigatório).' 
      });
      return;
    }

    setLoading(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append('resume_pdf', resumePdf);
    if (linkedinPdf) formData.append('linkedin_pdf', linkedinPdf);
    formData.append('github_url', githubUrl);
    formData.append('portfolio_url', portfolioUrl);
    formData.append('skills', JSON.stringify(skills));

    try {
      await axios.post('/api/resumes/optimize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setStatusMessage({ 
        type: 'success', 
        text: 'Dados enviados com sucesso! A IA está processando o currículo.' 
      });
      
      setResumePdf(null);
      setLinkedinPdf(null);
      setGithubUrl('');
      setPortfolioUrl('');
      setSkills([]);
    } catch (error: any) {
      console.error('Erro ao enviar formulário:', error);
      const apiErrorMessage = error.response?.data?.message;
      setStatusMessage({ 
        type: 'error', 
        text: apiErrorMessage || 'Erro ao conectar com o servidor. Tente novamente.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Otimizar Novo Currículo</h1>
        <p style={styles.subtitle}>
          Preencha as informações abaixo para que a IA gere uma versão otimizada para ATS.
        </p>
      </header>

      <form onSubmit={handleSubmit} style={styles.formCard}>
        
        {/* DOCUMENTOS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>1. Documentos PDF</h2>
          <div style={styles.grid2}>
            
            <div style={styles.fieldGroup}>
              <label style={styles.label}>
                Currículo Atual (PDF) <span style={styles.required}>*</span>
              </label>
              <div style={styles.fileUploadBox}>
                <input 
                  type="file" 
                  accept=".pdf" 
                  id="resume_pdf"
                  style={{ display: 'none' }} 
                  onChange={handleResumeChange}
                />
                <label htmlFor="resume_pdf" style={styles.fileUploadLabel}>
                  <Upload size={20} color="#2563eb" />
                  <span>{resumePdf ? resumePdf.name : 'Selecionar arquivo PDF'}</span>
                </label>
              </div>
            </div>

            <div style={styles.fieldGroup}>
              <label style={styles.label}>PDF do Perfil do LinkedIn (Opcional)</label>
              <div style={styles.fileUploadBox}>
                <input 
                  type="file" 
                  accept=".pdf" 
                  id="linkedin_pdf"
                  style={{ display: 'none' }} 
                  onChange={handleLinkedinChange}
                />
                <label htmlFor="linkedin_pdf" style={styles.fileUploadLabel}>
                  <FileText size={20} color="#0077b5" />
                  <span>{linkedinPdf ? linkedinPdf.name : 'Selecionar PDF do LinkedIn'}</span>
                </label>
              </div>
            </div>

          </div>
        </section>

        <hr style={styles.divider} />

        {/* LINKS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>2. Links e Presença Digital</h2>
          <div style={styles.grid2}>
            
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Link do GitHub</label>
              <div style={styles.inputWithIcon}>
                <Code2 size={18} color="#64748b" style={styles.inputIcon} />
                <input 
                  type="url" 
                  placeholder="https://github.com/seu-usuario"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  style={styles.input}
                />
              </div>
            </div>

            <div style={styles.fieldGroup}>
              <label style={styles.label}>Link do Portfólio / Site</label>
              <div style={styles.inputWithIcon}>
                <LinkIcon size={18} color="#64748b" style={styles.inputIcon} />
                <input 
                  type="url" 
                  placeholder="https://seu-portfolio.com"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  style={styles.input}
                />
              </div>
            </div>

          </div>
        </section>

        <hr style={styles.divider} />

        {/* HABILIDADES */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>3. Habilidades Principais</h2>
          <p style={styles.helperText}>Adicione suas hard skills e o tempo de experiência em cada uma.</p>

          <div style={styles.skillInputGrid}>
            <input 
              type="text" 
              placeholder="Ex: React, TypeScript, Node.js..."
              value={currentSkill}
              onChange={(e) => setCurrentSkill(e.target.value)}
              style={{ ...styles.input, flex: '2 1 200px', paddingLeft: '14px' }}
            />
            <input 
              type="number" 
              placeholder="Anos"
              min="0"
              max="50"
              value={currentYears}
              onChange={(e) => setCurrentYears(e.target.value)}
              style={{ ...styles.input, flex: '1 1 100px', paddingLeft: '14px' }}
            />
            <button type="button" onClick={handleAddSkill} style={styles.addSkillBtn}>
              <Plus size={18} />
              <span>Adicionar</span>
            </button>
          </div>

          {skills.length > 0 && (
            <div style={styles.skillsList}>
              {skills.map((item, index) => (
                <div key={index} style={styles.skillBadge}>
                  <span><strong>{item.name}</strong> ({item.years} {item.years === 1 ? 'ano' : 'anos'})</span>
                  <button 
                    type="button" 
                    onClick={() => handleRemoveSkill(index)} 
                    style={styles.removeSkillBtn}
                    title="Remover habilidade"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {statusMessage && (
          <div style={statusMessage.type === 'error' ? styles.errorMessage : styles.successMessage}>
            {statusMessage.type === 'error' ? <AlertCircle size={20} /> : <CheckCircle2 size={20} />}
            <span>{statusMessage.text}</span>
          </div>
        )}

        <div style={styles.footer}>
          <button type="submit" disabled={loading} style={styles.submitBtn}>
            <Send size={18} />
            <span>{loading ? 'Processando dados...' : 'Gerar Currículo com IA'}</span>
          </button>
        </div>

      </form>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '850px',
    margin: '0 auto',
    padding: '24px 16px',
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    color: '#0f172a',
  },
  header: {
    marginBottom: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#030712',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: '15px',
    color: '#64748b',
    margin: 0,
  },
  formCard: {
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    padding: '32px',
    border: '1px solid #e2e8f0',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.03)',
  },
  section: {
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '16px',
  },
  grid2: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#334155',
  },
  required: {
    color: '#ef4444',
  },
  fileUploadBox: {
    border: '2px dashed #cbd5e1',
    borderRadius: '10px',
    padding: '12px 16px',
    backgroundColor: '#f8fafc',
    cursor: 'pointer',
  },
  fileUploadLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#475569',
    fontWeight: '500',
  },
  inputWithIcon: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  inputIcon: {
    position: 'absolute',
    left: '12px',
  },
  input: {
    width: '100%',
    padding: '12px 12px 12px 40px',
    fontSize: '14px',
    borderRadius: '8px',
    border: '1px solid #cbd5e1',
    outline: 'none',
    backgroundColor: '#ffffff',
    boxSizing: 'border-box',
  },
  helperText: {
    fontSize: '13px',
    color: '#64748b',
    marginTop: '-8px',
    marginBottom: '12px',
  },
  skillInputGrid: {
    display: 'flex',
    gap: '10px',
    marginBottom: '16px',
    flexWrap: 'wrap',
  },
  addSkillBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: '#eff6ff',
    color: '#2563eb',
    border: '1px solid #bfdbfe',
    padding: '0 16px',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '14px',
    height: '42px',
  },
  skillsList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: '12px',
  },
  skillBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#f1f5f9',
    color: '#334155',
    padding: '6px 12px',
    borderRadius: '20px',
    fontSize: '13px',
    border: '1px solid #e2e8f0',
  },
  removeSkillBtn: {
    background: 'none',
    border: 'none',
    color: '#94a3b8',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    padding: 0,
  },
  divider: {
    border: 0,
    borderTop: '1px solid #f1f5f9',
    margin: '24px 0',
  },
  footer: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginTop: '24px',
  },
  submitBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#031b5b',
    color: '#ffffff',
    border: 'none',
    padding: '14px 28px',
    borderRadius: '10px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(3, 7, 18, 0.15)',
  },
  errorMessage: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#fef2f2',
    color: '#991b1b',
    padding: '12px 16px',
    borderRadius: '8px',
    marginTop: '16px',
    fontSize: '14px',
  },
  successMessage: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#f0fdf4',
    color: '#166534',
    padding: '12px 16px',
    borderRadius: '8px',
    marginTop: '16px',
    fontSize: '14px',
  },
};